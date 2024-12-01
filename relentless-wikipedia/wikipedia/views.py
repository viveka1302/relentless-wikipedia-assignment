from fastapi import FastAPI, Depends, HTTPException, APIRouter, Header, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from cockroachDB.factory import UsersTable, SearchResultsTable, SavedArticles
from .serializers import RegistrationDetails
import wikipediaapi
from typing import List
from cockroachDB.db_connection import conn
from langchainGemini.prompt import llm
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
SECRET_KEY = "123vivek_your_secret_key"
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

router= APIRouter(prefix="/bookmark-app")

# Registration endpoint
@router.post("/auth/register")
def register_user(regDetails: RegistrationDetails):
    data=regDetails.dict()
    userstable=UsersTable()
    result= userstable.get_email(email=data["primaryEmail"]).fetchall()
    if data["primaryEmail"] in result:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(data["passwd"])
    userstable.register(primaryEmail=str(data["primaryEmail"]), passwd_hash=hashed_password, firstName=data["firstName"], lastName= data["lastName"])
    return {"message": "User registered successfully"}

# Login endpoint
@router.post("/auth/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    userstable=UsersTable()
    user = userstable.get_email(str(form_data.username))
    userlist=user.fetchall()
    print(userlist)
    columns=user.keys()
    print(columns)
    columns=list(columns)
    print(columns)
    print(userlist)
    userdict= dict(zip(columns, userlist[0]))
    print(userdict)
    if not user or "passwd" not in userdict or not verify_password(form_data.password, userdict["passwd"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=50))
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint
@router.get("/article/search-articles")
def get_articles( wikiSearchQuery: str, token: str = Header(None, description="access token")):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        userstable=UsersTable()
        user= userstable.get_email(email=user_email)
        if (user_email is None) or (not user):
            raise HTTPException(status_code=401, detail="Invalid token")
        else:
            wiki_id = wikipediaapi.Wikipedia('bookmarks (vivekaprof@gmail.com)', 'en')
            wpage = wiki_id.page(wikiSearchQuery)
            if not wpage.exists():
                return {"message" : "requested page does not exist"}
            else:
                url= wpage.fullurl
                title=wpage.title
                summary= wpage.summary[0:2083]
                srt= SearchResultsTable()
                srt.save_results(title= title, url=url, summary=summary)
                results= srt.get_by_title(title=title)
                res_list= results.fetchall()
                columns= results.keys()
                columns= list(columns)
                resultsDict=dict(zip(columns, res_list[0]))
                return {"results": resultsDict}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Invalid token")
    
@router.post("/article/save-article")
def save_article(searchId: str, token: str= Header(None, description="access token")):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        userstable=UsersTable()
        user= userstable.get_email(email=user_email)
        if (user_email is None) or (not user):
            raise HTTPException(status_code=401, detail="Invalid token")
        else:
            srt= SearchResultsTable()
            results=srt.get_by_id(searchId=searchId)
            res_list= results.fetchall()
            columns= results.keys()
            columns= list(columns)
            resultsDict=dict(zip(columns, res_list[0]))
            userlist=user.fetchall()
            columns=user.keys()
            columns=list(columns)
            userdict= dict(zip(columns, userlist[0]))
            messages = [
                (
                    "system",
                    "List out 3-6 bullet points on new lines, which are categories to describe the following article. Each category is between one and two words. Do not use any filler sentences, simply list the categories and stop",
                ),
                ("human", f"There is an article titled {resultsDict['title']}, summarized as {resultsDict['summary']}."),
            ]
            ai_msg = str(llm.invoke(messages))
            print(ai_msg)
            match = re.search(r"content='(.*?)'", ai_msg, re.DOTALL)

            # Check if a match is found and print it
            if match:
                content_value = match.group(1)
                print(content_value)
            tags= content_value.split("\\n")
        
            print(tags)
            if len(tags)>6:
                tags=tags[0:5]
            elif len(tags)==0:
                raise HTTPException(status_code=404, detail="No tags generated")
            input_dict= {
                "title": resultsDict["title"],
                "url":resultsDict["url"],
                "summary":resultsDict["summary"],
                "savedby":userdict["userid"],
                "tags":str(tags)
            }
            saveArticle=SavedArticles()
            saveArticle.save_with_tags(**input_dict)
            return {"message" : "Article saved successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user unauthorized")
    
@router.get("/article/retrieve-articles")
def get_saved_articles(token: str= Header(None, description="access token")):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        user_email = payload.get("sub")
        print(user_email)
        userstable=UsersTable()
        user= userstable.get_email(email=user_email)
        if (user_email is None) or (not user):
            raise HTTPException(status_code=401, detail="Invalid token")
        else:
            userlist=user.fetchall()
            columns=user.keys()
            columns=list(columns)
            userdict= dict(zip(columns, userlist[0]))
            print(userdict)
            savedArticle=SavedArticles()
            data= savedArticle.get_by_user(userId=userdict["userid"])
            datalist= data.fetchall()
            print(datalist)
            col= data.keys()
            col= list(col)
            print(col)
            finalList=[]
            for i in datalist:
                dataDict= dict(zip(col, i))
                finalList.append(dataDict)
            return {"list of saved articles": finalList}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user unauthorized")
    
@router.patch("/article/update-tags")
def update_tags(articleId:str, oldTag:str, newTag:str, token:str= Header(None, description="access token")):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        userstable=UsersTable()
        user= userstable.get_email(email=user_email)
        if (user_email is None) or (not user):
            raise HTTPException(status_code=401, detail="Invalid token")
        else:
            savedArticle=SavedArticles()
            article= savedArticle.get_by_id(articleId=articleId)
            articlelist= article.fetchall()
            print(articlelist)
            col= article.keys()
            col= list(col)
            print(col)
            articleDict= dict(zip(col, articlelist[0]))
            print(articleDict)
            tags= articleDict["tags"]
            print(tags)
            if oldTag in tags:
                tags=tags.replace(oldTag,  newTag)
                print(tags)
                savedArticle.update_tag(articleid=articleId, tags=tags)
                return {"message": f"tag updated successfully from {oldTag} to {newTag}"}
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tag not found")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user unauthorized")
    