from django.db import models
from typing import List
from jsonfallback.fields import FallbackJSONField
from pydantic import BaseModel, Field

# Create your models here.

class ThreadTask(models.Model):
    task = models.CharField(max_length=30, blank=True, null=True)
    is_done = models.BooleanField(blank=False,default=False )
    result = FallbackJSONField(max_length=1024, blank=True, null=True)

class Result(BaseModel):
    code : int
    text : str

class Resultbundle(BaseModel):
    results:List[Result]
