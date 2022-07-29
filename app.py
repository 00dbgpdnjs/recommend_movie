import pickle # pickle로 덤프한 파일 가져오려고

# streamlit : 간단히 웹 페이지 만듬
# 판다스, 맵플럴리, 넘파이, 사이킷런 등의 데이터 사이언스 관련을 웹으로 보기 유용
# ******* $ streamlit run app.py ********
import streamlit as st 

# $ pip install tmdbv3api
# tmdb 사이트에서 영화 정보 가져오기
from tmdbv3api import Movie, TMDb

# 객체 생성
movie = Movie()
tmdb = TMDb()

# api : 우리 프로그램이 서버에 어떤 데이터를 요청하면 서버에서는 그 요청에 따른 데이터 반환. 이 때 서로 통신할 수 있게 해줌
# api가 누구에게나 공개되는 경우도 있고, api key 를 요구할 수 있음. 
# 키가 없으면 api 이용 못하도록 제한.
# 사용자 마다 서로 다른 api 키를 발급 받아야함
tmdb.api_key = '3cf1429ba50e278bdab443bf6d68e698' 
tmdb.language = 'ko_KR'

# 아래 함수 이해 안가면 같은 디렉토리에 있는 주피터 파일에 더 자세히 설명됨
# 영화의 제목을 입력받으면 코사인 유사도를 통해서 가장 유사도가 높은 상위 10개의 영화 목록 반환
def get_recommendations(title):
    # 영화 제목을 통해서 전체 데이터 기준 그 영화의 idx 값 얻기
    idx = movies[movies['title'] == title].index[0] # index가 배열이라서 그냥 첫번째 인덱스라고 하면 영화 인덱스임

    # 코사인 유사도 매트릭스 (cosine_sim) 에서 영화idx 에 해당하는 데이터를 (idx, 유사도) 형태로 얻기
    # 왜냐면 그냥 유사도만 가져오면 무슨 영화인지 알 수 없음
    sim_socres = list(enumerate(cosine_sim[idx])) # 위에꺼를 인덱스와 함께 보기 / 3은 자기 자신이니까 1 / (인덱스, 유사도)인 pair 형태를 다시 한 번 리스트로 감싸줌 (굳이 안감싸도 되긴함)
    
    # x[1] 즉 유사도를 기준으로 내림차순
    sim_socres = sorted(sim_socres, key=lambda x: x[1], reverse=True) # x[0]:idx, x[1]:유사도
    
    # 자기 자신을 제외한 10개의 추천 영화를 슬라이싱
    sim_socres = sim_socres[1:11]
    
    # 추천 영화 목록 10개의 인덱스 정보 추출
    movie_indices = [i[0] for i in sim_socres] # 인덱스만 추출
    
    # 인덱스 정보를 통해 영화 제목 추출
    images = []
    titles = []
    for i in movie_indices:
        id = movies['id'].iloc[i]

        # 영화 id를 전달하면 그 영화의 상세 정보 줌
        # tmdb movie details를 검색하고 get - The Movie Database API 로 들어가면 Responses에 details가 어떤 것들이 있는지 나옴 https://developers.themoviedb.org/3/movies/get-movie-details
        details = movie.details(id) 

        # 영화 Identity 와 같이 details['poster_path'] 가 None 이면 str인 base_url과 합칠 수 없어서 에러가 발생하므로 예외처리해야함
        # 이미지를 가져오는 과정에서 poster_path가 없다면 no_image.jpg 보여주기
        image_path = details['poster_path']
        if image_path:
            image_path = 'https://image.tmdb.org/t/p/w500' + image_path
        else:
            image_path = 'no_image.jpg'

        # image path가 full url 이 아니므로 base url 와 합쳐야함
        #images.append('https://image.tmdb.org/t/p/w500' + details['poster_path']) # 예외 처리 전
        images.append(image_path)
        titles.append(details['title']) # 매개변수로 받았는데 또 받는 이유는 한국말 버전을 위해..??

    return images, titles

movies = pickle.load(open('movies.pickle', 'rb'))
cosine_sim = pickle.load(open('cosine_sim.pickle', 'rb'))

st.set_page_config(layout='wide') # wide : 이거 안하면 화면이 조그맣게 나오므로 전체화면 모드로

# 헤더 설정 : 화면 상단의 제목 역할
st.header('happyflix')

movie_list = movies['title'].values # title열의 값만 

# 콤보 박스에서 선택한 영화 제목 저장
title = st.selectbox('Choose or write a movie you like', movie_list)
if st.button('Recommend'): # Recommend 라는 버튼을 클릭하면
    with st.spinner('Please wait...'): # 아래 문장들이 끝날때까지 프로그레스 바
        images, titles = get_recommendations(title)

        idx=0
        for i in range(0,2):
            cols = st.columns(5) # 5개의 컬럼을 만들어줌
            for col in cols : # 각 컬럼에
                col.image(images[idx]) # 웹에 이미지 넣어줌
                col.write(titles[idx]) # 웹에 제목 쓰기
                idx += 1 # 다음 컬럼에서는 다음 인덱스에 해당하는 데이터를 가지고 쓰기 

