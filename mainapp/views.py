from django.shortcuts import render,HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser,MultiPartParser,FormParser
from .models import *
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max
from .serializer import *
from backend import settings
from email.message import  EmailMessage
import ssl
import smtplib
import random
from datetime import datetime
import pytz
import base64
utc=pytz.UTC


def authenticateUser(email,password):
    print(email)
    print(password)
    obj=User.objects.filter(email=email)
    if len(obj)==0 :
        return False
    obj=obj[0]
    if obj.password==password:
        return True
    return True
    return False
    
def evalVal(a):
    if(type(a)!=type("dfjk")) :
        return a
    for i in a:
        if i!='.'  and  not (ord(i)>=48 and ord(i)<=57):
            return a
    return eval(a)
def sendMail(email_receiver,otp):
    email_sender="ashutoshsinghas2409@gmail.com"
    email_password='mekxceifwhwwcevg'
    subject="OTP generation"
    body="Your otp for ebid is "+str(otp)
    em=EmailMessage()
    em["From"]=email_sender
    em["To"]=email_receiver
    em['Subject']=subject
    em.set_content(body)
    context=ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_receiver,em.as_string())
    print("done")
class MakeOTPView(APIView):
    serializer_class=OTPSerializer
    def post(self,request):
        print("HIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIiii")
        params="work kr lo "
        if  "params" in request.data:
            params=request.data["params"]
            print("HIII")
        else :
            print("NOOOOOOOOOOoooo")
            return Response(data={"can not handle this request"})
        print(params)
        if "email" in params:
            myemail=params["email"]
            print(myemail)
            myotp=random.randint(100000,999999)
            sendMail(myemail,myotp)
            serializer=OTP(email=myemail,otp=myotp)
            serializer.save()
            return Response(data={"right":1})
        else :
            print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLllllll")
            # return Response(data={'wrong':1111})
class CreateUser(APIView):
    serializer_class=UserSerializer
    def post(self,request):
        print("CCCCCCCCCCCCCCCCCCCCCCCCCCc")
        if "params" in request.data:
            params=request.data["params"]
        else:
            return Response(data="invalid arguments")
        print(params)
        if "email" in params:
            print("email is ok")
        if "password" in params:
            print("password is ok")
        if "otp" in params:
            print("otp is ok")
        if "fName" in params:
            print("fName is ok")
                
        if "email" in  params and "password" in params and "fName" in params and "otp" in request.data["params"]:
            myotp=request.data["params"]["otp"]
            mymail=request.data["params"]["email"]
            userObj=User.objects.filter(email=mymail)
            if(len(userObj)):
                return Response(data={"User already exist":1})
            obj=OTP.objects.filter(email=mymail)

            if(len(obj)):
                obj=obj[0]
            else:
                return Response(data={"no otp has been sent to this email":1})
            if obj.otp==myotp:
                serializer=User(email=request.data["params"]["email"],password=request.data["params"]["password"],firstName=request.data["params"]["fName"])
                serializer.save()
                # obj.delete()
                return Response(data={"isAuthenticated":1})
            else:
                return Response(data={"Wrong OTP":1})
        return Response(data={"Invalid Request":1})
    
class CreateRoomView(APIView):
    serializer_class=AuctionRoom
    def post(self,request):
        params=request.data["params"]
        if 'email' and 'password' and  'productName' and   'productDetail' and 'bidDiff' in params :
            myEmail=str(params["email"])
            myPassword=str(params["password"])
            myProductName=str(params["productName"])
            myProductDetail=str(params["productDetail"])
            myBidDiff=eval(params["bidDiff"])
            
            if type(evalVal(str(myBidDiff)))==type(1):
                myBidDiff=evalVal(str(myBidDiff))
            else:
                return Response(data={"invalid Bid difference"})
            obj=User.objects.filter(email=myEmail)
            if len(obj)==0 or obj[0].password!=myPassword:
                return Response(data={"wrong User":1})
            serializer=AuctionRoom(
                roomOwner=obj[0],
                productName=myProductName,
                productDetail=myProductDetail,
                bidDiff=myBidDiff,
                )
            if "upperLimit" in params and type(evalVal(params["upperLimit"]))==type(5):
                serializer.upperLimit=params["upperLimit"]
            if "lowerLimit" in params and type(evalVal(params["lowerLimit"]))==type(5):
                serializer.upperLimit=params["lowerLimit"]
            # if "startTime" in params :
            #     serializer.startTime=params["startTime"]
            # if "endTime" in params:
            #     serializer.endTime=params["endTime"]
            # if "productPhot" in params:
            #     serializer.productPhoto=params["produtPhoto"]
            serializer.save()
            return Response(data={"room created Successfully":1})
        else:
            return Response(data={"invalid Request":1})
class MakeBidView(APIView):
    def post(self,request):
        if "params" in request.data:
            params=request.data["params"]
            print(params)
        else:
            return Response(data={"no params"})
        if  ("email" in params) and ("password" in params) and ("bidPrice" in params) and ("roomId" in params):
            myEmail=params["email"]
            myPassword=params["password"]
            myBidPrice=params["bidPrice"]
            myRoomId=params["roomId"]
            userObj=User.objects.filter(email=myEmail)
            #is user valid
            if len(userObj)==0 or userObj[0].password!=myPassword:
                return Response(data={"wrong User"})
            userObj=userObj[0]
            #is auction room valid
            roomObj=AuctionRoom.objects.filter(roomId=myRoomId)
            if len(roomObj)==0:
                return Response(data="Invalid room")
            roomObj=roomObj[0]
            #is room owner is bidding
            if(roomObj.roomOwner==userObj):
                return Response(data={"cannot bid in your own room"})
            #is it right time to bid
            now=datetime.now()
            
            startTime=roomObj.startTime.replace(tzinfo=utc)
            # endTime=roomObj.endTime.replace(tzinfo=utc)
            now=now.replace(tzinfo=utc)
            # if now<startTime or now>endTime:
            #     return Response(data={"You are either too early or too late"})    
            if now<startTime :
                return Response(data={"You are either too early or too late"})    
            # is bid value correct
            maxBid=Bid.objects.filter(room=roomObj)
            if len(maxBid):
                maxBid=maxBid.aggregate(Max('bidPrice'))["bidPrice__max"]
            else:
                maxBid=roomObj.lowerLimit-roomObj.bidDiff
            print(type(evalVal(myBidPrice)))
            if  type(evalVal(myBidPrice))!=type(4) or maxBid+roomObj.bidDiff>evalVal(myBidPrice):
                return Response(data={"cannot bid this amount"})
            serializer=Bid(user=userObj,room=roomObj,bidPrice=myBidPrice)
            serializer.save()
            return Response(data={"everything is well"})
        return Response(data="Not valid argument")
    
class GetRoomView(APIView):
    def post(self,request):

        if "params" in request.data:
            params=request.data["params"]
        else :
            return Response(data={"no params"},status=status.HTTP_400_BAD_REQUEST)
        if "roomId" in params:
            print(params["roomId"])
            room=AuctionRoom.objects.filter(roomId=params["roomId"])
            print(room)
            if(len(room)):
                room=room[0]
            else :
                return Response(status=status.HTTP_400_BAD_REQUEST)
            resData={}
            resData["productName"]=room.productName
            resData["productDetail"]=room.productDetail
            resData["bidDiff"]=room.bidDiff
            resData["minBid"]=room.lowerLimit
            resData["endTime"]=room.endTime
            resData["img"]=room.productPhoto.url
            return Response(data=resData)
        else:
            return Response(data="No room Exists" ,status=status.HTTP_400_BAD_REQUEST)
class Top10(APIView):
    def post(self,request):

        if "params" in request.data:
            params=request.data["params"]
        else :
            return Response(data={"no params"},status=status.HTTP_400_BAD_REQUEST)
        if "roomId" in params:
            roomId=params["roomId"]
            room=AuctionRoom.objects.filter(roomId=roomId)
            if len(room)==0:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            room=room[0]
            print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTt")
            obj=Bid.objects.filter(room=room).order_by('-bidPrice')
            print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSs")
            resData=list()
            for i in range(0,min(10,len(obj))):
                print("The user is ")
                temp=obj[i]
                resData.append([temp.user.firstName,temp.bidPrice])
                
                # print(temp.user)
                # print(temp.user.firstName)
                # print(temp.bidPrice)
            return Response(data=resData,status=status.HTTP_200_OK) 

        return Response(status=status.HTTP_200_OK)

class UserRooms(APIView):
    def post(self,reqeuest):
        if "params" in reqeuest.data:
            params=reqeuest.data["params"]
        else :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if "email" in params and "password" in params:
            email=params["email"]
            password=params["password"]
            if authenticateUser(email,password)!=True:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            userObj=User.objects.filter(email=email)[0]
            auctionObj=AuctionRoom.objects.filter(roomOwner=userObj).order_by('-startTime')
            resData=list()
            for i in auctionObj:
                resData.append(i.productName)
            return Response(data=resData,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
class UserBids(APIView):
    def post(self,reqeuest):
        if "params" in reqeuest.data:
            params=reqeuest.data["params"]
        else :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if "email" in params and "password" in params:
            email=params["email"]
            password=params["password"]
            if authenticateUser(email,password)!=True:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            userObj=User.objects.filter(email=email)[0]
            bidObj=Bid.objects.filter(user=userObj)
            resData=list()
            for i in bidObj:
                resData.append(i.room.productName)
                # print(i.room.productName)
            return Response(data=resData,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
class UserInfo(APIView):
    def post(self,reqeuest):
        if "params" in reqeuest.data:
            params=reqeuest.data["params"]
        else :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if "userId" in params:
            
            userId=params["userId"]
            print(userId)
            userObj=User.objects.filter(userId=userId)
            if len(userObj)==0:
                return Response(data={"message":"This user doesn't exist"},status=status.HTTP_404_NOT_FOUND)
            userObj=userObj[0]
            auctionObj=AuctionRoom.objects.filter(roomOwner=userObj)
            bidObj=Bid.objects.filter(user=userObj)
            resData={"fName":userObj.firstName,
                     "lName":userObj.lastName,
                     "address":userObj.address,
                     "img":userObj.userPhoto.url,
                     "totalAuction":len(auctionObj),
                     "totalBids":len(bidObj),
                     }
            return Response(data=resData,status=status.HTTP_200_OK)
        return Response(data={"message":"Something went wrong"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class Products(APIView):
    def post(self,request):
        page=1
        if "params" in request.data  and "page" in request.data["params"]:
            page=request.data["params"]["page"]
        if type(page)!=type(5):
            page=1
        pageSize=8
        obj=AuctionRoom.objects.all()
        resData=list()
        for i in range((page-1)*pageSize,min(page*pageSize,len(obj))):
            resData.append({"productName":obj[i].productName,"productDetail":obj[i].productDetail,
                            "img":obj[i].productPhoto.url,"productId":obj[i].roomId
                            
                            })
            print(obj[i].productPhoto.url)
            print(i)
            # for k in obj[i].productPhoto:
            #     print(k,sep="")

        return Response(data=resData,status=status.HTTP_200_OK)
        
            

class Authenticate(APIView):
    def post(self,request):        
        if "params" in request.data:
            params=request.data["params"]
            if "email" in params and "password" in params and authenticateUser(params["email"],params["password"]):
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
        

    

            
            
            
            
            





        

        

