from pydantic import BaseModel, Field, EmailStr

class RegistrationDetails(BaseModel):
    primaryEmail: EmailStr = Field(description= "user email Id", examples=["abcw2@gmail.com"])
    passwd: str= Field(description="unhashed user password")
    firstName: str= Field(examples=["Vivek"])
    lastName: str= Field(examples=["Anand"])

class LoginDetails(BaseModel):
    primaryEmail: EmailStr = Field(description= "user email Id", examples=["abcw2@gmail.com"])
    passwd: str= Field(description="unhashed user password")