from .db_connection import conn, users_table, sr_table, saved_article_table
from datetime import datetime
from sqlalchemy import insert, text, update

class UsersTable():
    
    def register(self, primaryEmail, passwd_hash, firstName, lastName):
        createdAt=datetime.today().strftime("%s")
        userID= "USR"+createdAt
        params={
            "userid": userID,
            "primaryemail": primaryEmail,
            "passwd": passwd_hash,
            "firstname": firstName,
            "lastname": lastName,
            }
        table=users_table
        print(table)
        try:
            query=table.insert().values(**params)
            query_results= conn.execute(query)
            conn.commit()
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()
        
    
    def get_email(self, email):
        try:
            query= "SELECT userID, primaryEmail, passwd, firstName, lastName FROM userdata WHERE primaryEmail= :email"
            emaildict={"email": email}
            query_results= conn.execute(text(query), emaildict)
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()
        

class SearchResultsTable():
    def save_results(self, title, url, summary):
        createdAt=datetime.today().strftime("%s")
        searchID= "SER"+createdAt
        params={
            "searchid": searchID,
            "title": title,
            "url": url,
            "summary": summary
        }
        table= sr_table
        try:

            query= table.insert().values(**params)
            query_results= conn.execute(query)
            conn.commit()
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()
        
    def get_by_title(self, title):
        try:
            title=title
            query= "SELECT * FROM SearchResults WHERE title= :title"
            query_results= conn.execute(text(query), {"title":title})
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()
        
    def get_by_id(self, searchId):
        try:
            
            query= "SELECT * FROM SearchResults WHERE searchid= :searchid"
            query_results= conn.execute(text(query), {"searchid":searchId})
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()

class SavedArticles():
    def save_with_tags(self, **kwargs):
        createdAt=datetime.today().strftime("%s")
        articleId= "ART"+createdAt
        params={
            "articleid": articleId,
            **kwargs
        }
        table= saved_article_table
        try:

            query= table.insert().values(**params)
            query_results= conn.execute(query)
            conn.commit()
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()
    def get_by_user(self, userId):
        try:
            query= "SELECT * FROM savedarticles WHERE savedby= :userid"
            query_results= conn.execute(text(query), {"userid":userId})
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()
    def get_by_id(self, articleId):
        try:
            
            query= "SELECT * FROM savedarticles WHERE articleid= :articleid"
            query_results= conn.execute(text(query), {"articleid":articleId})
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()
    def update_tag(self, articleid, tags:str):
        table= saved_article_table
        try:
            query= table.update().where(table.c.articleid== articleid).values(tags=tags)
            query_results= conn.execute(query)
            conn.commit()
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()


    def user_activity(self):
        try:
            query= "SELECT * FROM savedarticles ORDER BY createdat DESC LIMIT 10;"
            query_results= conn.execute(text(query))
            return query_results
        except Exception as e:
            print(e)
            conn.rollback()
