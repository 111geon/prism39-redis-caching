
## 💾 Redis 소개

### 개요

- Remote Dictionary Server
- **주로 캐시 용도로 쓰는 In-Memory 저장소**
    - 캐시 : 자주 사용되는 데이터를 임시로 보관하여 더 빠르게 응답하기 위해 사용하는 것.
    - RDBMS : 데이터를 찾기 위해 인덱싱을 하고, 이 인덱스는 주로 BTree를 사용한다.
    - Tree의 장단점 : Range Search가 용이하다. 느리다.

### 특징

- Key-Value 형식
    - **hash 기반의 key-value 저장 방식** -> 검색/저장/삭제가 O(1)만에 일어남.
    - range 검색이 안됨.
- In-Memory
    - RDBMS는 인덱스-데이터를 디스크에 넣어놓고 필요할 때 메모리에 로딩하여 사용.
    - RDBMS는 Tree 구조로 인덱싱을 한다는 것과 디스크에 접근해야 한다는 점 때문에 느림.
    - Redis는 모든 데이터를 memory에 올려놓고 그걸 한번씩 디스크에 flush해서 백업만 하는 구조.
    - **Redis가 담을 수 있는 용량 == 물리 메모리 사이즈(RAM)**
    - RDBMS와 비교했을 때 훨씬 빠름
- Single Threaded
    - **Lock을 구현하기에 편함.**
        - DB는 multi-threaded 구조이기 때문에 락이 없으면 송금이 두번될 수가 있음(DB단에서 막을 수는 있음).
        - redis는 single thread이기 때문에 모든 요청이 순서대로 처리가 되어(FIFO은 아닐 순 있지만, 적어도 중복처리>는 안됨) 동기화 문제가 없음

### 용도

- 캐싱
    - **응답이 더 빠름**.
    - cluster 구성이 가능하여 **RDBMS의 부하를 경감할 수 있음**.
        - 하나의 DB storage에 접근하는 DB server를 여러개 두어(클러스터링 하여) 하나의 DB server에 에러가 났을 때 다른 Active 상태의, 또는 Stand-by 상태였던 애를 Active로 만든 다른 DB 서버를 이용하여 **서비스가 멈추지 않도록 DB 서버를 분산**시키는 것.
- Lock
    - setnx를 이용하여 **한 transaction이 여러 tx가 중복처리하면 안되는 영역을 쓰고 있으면 다른 tx는 원천적으로 접근할 수 없도록 함**.
        - setnx : 해당 key에 데이터가 없을 때만 set하도록 함.
        - 락을 건 애가 오류나서 뻗어도 setnxex를 써서 기본 expire 시간을 주면 알아서 풀리게 할 수 있다.
        락 거는 일을 서버 자체에서 안하고 redis에 위임해서 하는 이유는 요즘 서버가 멀티 인스턴스이기 때문!

---

#@ 🧩문제

### Caching

- 95만 개의 sample data를 이용하여 어떻게 캐싱을 하면 큰 IO 작업으로 부터 DB의 load를 줄여줄 수 있을까
- 실제로 IO 속도를 얼마나 줄일 수 있을까
- RDBMS는 PostgreSQL을 이용
- In-Memory Caching은 Redis를 이용
- 일단 네트워크 보틀넥은 발생하지 않는다고 가정하고 localhost에서 진행

![PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_13-15-09.png](PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_13-15-09.png)

### 과제

성능 테스트: Redis를 쓰면 실제로 빨라질까? 

- adaptive 방식이랑 fixed 방식을 실제 실험해서 비교해보자. 오버헤드 코스트 비교
- case를 여러가지 만들어보자
    - 없는 거를 가져오라고 했을 때 어떻게 코스트가 생기는지
    - redis에 1년치만 넣어놓고 일부러 그 2년전 데이터를 요구했을 때 어떻게 되는지.

### Caching Policy

- 어느 포인트에서 캐싱을 하는 것이 더 빠를지:
    1. DB가 캐시에 직접 요청하는 경우에는 원데이터에서 매핑하기 전에 캐싱하는 게 나을듯
    2. 처음에 Redis를 들렸다가 DB로 가는 경우:
        1. mapping 된 이후의 회사 아이디를 기준으로 캐싱
        2. 아예 최종 데이터 다 나오고 캐싱
- redis와 sql이 따로 있는 게 좋을지, extension을 쓰는 게 좋을지

### Starting Point

- 아예 캐싱 안하는 방식과 fixed 방식으로 캐싱했을 때를 비교하는 거 부터 시작
- 어떤 형태로 Redis에 저장을 해야.. key, field, value.. 시계열 데이터에 대표적인 Sorted Set? Set? Hash Set?

---

## Case Study

![PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_14-59-37.png](PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_14-59-37.png)

![PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_13-27-18.png](PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_13-27-18.png)

### REDIS SET

![PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_15-02-15.png](PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_15-02-15.png)

- 년도 별로 모두 쪼갰었는데 년도별로 쪼개는 작업이 벡터화하기 어렵고 벡터화하려면 년도만 담는 추가적인 메모리 공간이 필요하게되고, 굳이 시간과 공간을 투자할 만큼 효용이 있는 것 같지 않다.

![PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_15-04-20.png](PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_15-04-20.png)

- HashSet: listingid로 키를 만들고 field에는 price, Moving Average 같은 걸 구분하고 value에 값을 넣는걸로.. 최대한 loop을 안돌리고 벡터로 처리하도록 하였으나 redis 와 통신할 때는 벡터화가 완전하게 가능하지는 않았다.

### REDIS GET

![PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_15-06-42.png](PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_15-06-42.png)

![PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_15-07-53.png](PRISM39%E1%84%8B%E1%85%A6%E1%84%89%E1%85%A5%E1%84%82%E1%85%B3%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%85%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%86%AF%E1%84%8B%E1%85%B5%20%E1%84%8B%E1%85%B5%E1%86%BB%E1%84%8B%E1%85%A5%E1%86%BB%E1%84%89%E1%85%B3%E1%86%B8%E1%84%82%E1%85%B5%E1%84%83%E1%85%A1%20-%20%E1%84%87%E1%85%A2%E1%86%A8%E1%84%8B%E1%85%A6%E1%86%AB%E1%84%83%20a180d0b17ec348be9ca89763da963dc0/_2021-07-01_15-07-53.png)

- 년도별로 모두 쪼개는 경우 한 여러개의 key를 가져올 때 너무 느려지기 때문에 SET과 마찬가지로 GET에서도 비효율적임을 알 수 있었음.
- listingid로만 쪼갠 경우 여러개의 key를 가져올 때 훨씬 유리했고 특정키를 가져오는 속도에서도 우수한 성능을 유지하고 있기 때문에 회사별로만 쪼개놓아도 충분히 효율적일 것 같음.

### 잠정 결론

- 한 request에 여러 key가 들어오는 경우에는 통째로 저장하는 것이 유리하고,
- 한 request 안에 key 수는 적으나 많은 수의 request가 들어오는 경우 쪼개는 것이 유리할 것으로 생각된다.

### FeedBack

- 네트워크 세팅 상태에 따라 달라질 것
- 하드웨어 세팅 상태에 따라 달라질 것
- SQL indexing 상태에 따라 다를 것
- 렘이 병렬로 늘어났을 때 달라질 것
- 탐색 싱글셀이 두배로 늘어났을 때 시간도 두배로 늘어나는지

---

# 🏔️추가 과제

- SQLAlchemy Core 를 이용한 Query 성능 향상
- Pandas Dataframe의 Vectorization을 이용하여 속도 향상 (Python for loop를 사용하지 않기)
- Asyncio를 이용한 비동기 처리로 DB Query 성능 향상
