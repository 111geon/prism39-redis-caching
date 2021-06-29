import time
import pandas
import pickle

from fastapi        import APIRouter, Depends, status
from sqlalchemy.orm import Session
import redis
import pyarrow

import database, models


router = APIRouter(
    prefix = "/test_data_1",
    tags   = ["test_data_1"]
)
get_db = database.get_db


@router.get("", status_code=status.HTTP_200_OK)
def get_all(db: Session = Depends(get_db)):

    result = {}

    #1. SQL: Query Set
    start       = time.time()
    db_queryset = db.query(models.TestData1).all()

    result.update(
        {
            "db_queryset": 
                [
                    time.time() - start,
                    str(type(db_queryset)),
                    len(db_queryset)
                ]
        }
    )

    #2. SQL: DataFrame
    start = time.time()
    db_df = pandas.read_sql_query('select * from "test_data_1"', con=database.engine)
 
    result.update(
        {
            "db_dataframe": 
                [
                    time.time() - start,
                    str(type(db_df)),
                    len(db_df)
                ]
        }
    )

    #3. Redis: Sorted Set
    start = time.time()
    r = redis.Redis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)
    redis_dict = {}

    [ 
        redis_dict.update(
            {k: r.zrange(k, 0, -1, withscores=True, score_cast_func=int)}
        ) for k in r.scan_iter() 
    ]
 
    result.update(
        {
            "redis_sortedset": 
                [
                    time.time() - start,
                    str(type(redis_dict)),
                    len(redis_dict)
                ]
        }
    )

    #4. Redis: GET DataFrame
    start = time.time()
    r = redis.Redis(host='localhost', port=6379, db=1)
    context = pyarrow.default_serialization_context()
    redis_df_total = context.deserialize(r.get("total_data"))
    
    result.update(
        {
            "redis_dataframe_total": 
                [
                    time.time() - start,
                    str(type(redis_df_total)),
                    len(redis_df_total)
                ]
        }
    )

    #5. Redis: HGET "listingid:price year DataFrame"
    start = time.time()
    r = redis.Redis(host='localhost', port=6379, db=2)
    context = pyarrow.default_serialization_context()
    redis_df_div = {}
    
    for key in r.scan_iter():
        key = key.decode('utf-8')
        values = {a.decode('utf-8'): context.deserialize(b) for a, b in r.hgetall(key).items()}
        redis_df_div.update({key: values})

    result.update(
        {
            "redis_dataframe_divided": 
                [
                    time.time() - start,
                    str(type(redis_df_div)),
                    len(redis_df_div)
                ]
        }
    )

    #6. Case4 vs Case5
    case4vscase5 = {}

    start = time.time()
    r = redis.Redis(host='localhost', port=6379, db=1)
    context = pyarrow.default_serialization_context()
    df_case4 = context.deserialize(r.get("total_data"))
    df_case4 = df_case4.loc[df_case4['listingid'] == "2596570"]
    df_case4 = df_case4.loc[df_case4['date'].str.startswith("2020", na=False)]

    case4vscase5.update({'case4_time': time.time() - start, "case4_result": df_case4.head()})

    start = time.time()
    r = redis.Redis(host='localhost', port=6379, db=2)
    context = pyarrow.default_serialization_context()
    df_case5 = context.deserialize(r.hget("2596570:price", "2020"))

    case4vscase5.update({'case5_time': time.time() - start, "case5_result": df_case5.head()})

    result.update({'Case4 vs Case5': case4vscase5})

    return result 


@router.post("", status_code=status.HTTP_201_CREATED)
def create_redis():

    with open("example_data/test_data1.pkl", "rb") as f:
        data_1 = pickle.load(f)
  
    # data type 변환
#    data_1['date'] = pandas.to_datetime(data_1['date']).astype(int)/10**9  
    data_1['date'] = data_1['date'].apply(lambda x:  
        x.year*10**10 + x.month*10**8 + x.day*10**6 + x.hour*10**4 + x.minute*10**2 + x.second    
    )  
    data_1 = data_1.astype({'date': str, 'listingid': str})  
    result = {}

#    #1. Dataframe의 각 요소를 Sorted Set 형태로 저장
#    start = time.time()  
#    r = redis.Redis(host='localhost', port=6379, db=0)  
#    [r.zadd(x+":price", {y: z}) for x, y, z in zip(data_1['listingid'], data_1['value'], data_1['date'])] 
#    result.update({"Dataframe의 각 요소를 Sorted Set 형태로 저장":time.time() - start})
#       
#    #2. Dataframe 통째로 SET
#    start = time.time()  
#    r = redis.Redis(host='localhost', port=6379, db=1)
#    context = pyarrow.default_serialization_context()
#    r.set("total_data", context.serialize(data_1).to_buffer().to_pybytes())
#    result.update({"Dataframe을 통째로 SET":time.time() - start})
  
    #3. Dataframe을 쪼개서 HSET
    start = time.time()
    r = redis.Redis(host='localhost', port=6379, db=2)
    context = pyarrow.default_serialization_context()
    years = [ str(year) for year in range(2009, 2021) ]

    print(data_1.groupby("listingid"))

#    for listingid, df in data_1.groupby("listingid"):
#        values = {}
#        for year in years:
#            divided_df = df.loc[df['date'].str.startswith(year, na=False)]
#            values.update({year: context.serialize(divided_df).to_buffer().to_pybytes()})
#        r.hmset(listingid+":price", values)

    result.update({"Dataframe을 쪼개서 HSET":time.time() - start})

    return result
