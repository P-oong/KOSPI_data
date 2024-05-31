import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="현풍의 KOSPI와 원자재 상관관계 분석",
    page_icon="📈"
)

# 원자재 티커 심볼 목록
selected_commodities = {
    'Gold': 'GC=F',
    'Copper': 'HG=F',
    'Oats': 'ZO=F',
    'Natural Gas': 'NG=F',
    'Silver': 'SI=F',  # 추가된 원자재
    'Platinum': 'PL=F',  # 추가된 원자재
    'Crude Oil': 'CL=F',  # 추가된 원자재
    'Wheat': 'ZW=F',  # 추가된 원자재
    'Soybeans': 'ZS=F'  # 추가된 원자재
}

# 데이터 수집 함수
@st.cache
def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data['Close']

def plot_data(commodity_data, kospi_data, title):
    plt.figure(figsize=(14, 8))
    plt.plot(kospi_data.index, kospi_data, label='KOSPI', color='black', linewidth=2)
    for name, data in commodity_data.items():
        plt.plot(data.index, data, label=name, linewidth=1)
    plt.title(title)
    plt.xlabel('Year')
    plt.ylabel('Price')
    plt.legend()
    st.pyplot(plt)

# Streamlit 앱 레이아웃
st.title('KOSPI와 원자재 상관관계 분석')
st.markdown('이 앱은 KOSPI와 원자재 간의 상관관계를 분석하고 시각화합니다.')

# 사용자 입력: 데이터 수집 기간 설정
start_date = st.date_input('시작 날짜', pd.to_datetime('2004-01-01'))
end_date = st.date_input('종료 날짜', pd.to_datetime('2024-01-01'))

# 원자재 선택 (한 가지 또는 두 가지)
commodities = st.multiselect('원자재를 선택하세요 (한 가지 또는 두 가지)', list(selected_commodities.keys()), default=list(selected_commodities.keys())[:1])

# 데이터 수집
kospi_data = fetch_data('^KS11', start_date, end_date)
commodity_data = {commodity: fetch_data(selected_commodities[commodity], start_date, end_date) for commodity in commodities}

# 데이터 결측치 처리 (선형 보간법)
kospi_data = kospi_data.interpolate(method='linear')
for commodity in commodities:
    commodity_data[commodity] = commodity_data[commodity].interpolate(method='linear')

# 월별 데이터로 변환 (월별 평균)
monthly_data = pd.DataFrame({'KOSPI': kospi_data}).join(pd.DataFrame(commodity_data)).resample('M').mean()

# 코스피 데이터 추출
kospi_data_month = monthly_data['KOSPI']

# 데이터 정규화
kospi_data_normalized = (kospi_data_month - kospi_data_month.min()) / (kospi_data_month.max() - kospi_data_month.min())
commodity_data_normalized = {commodity: (monthly_data[commodity] - monthly_data[commodity].min()) / (monthly_data[commodity].max() - monthly_data[commodity].min()) for commodity in commodities}

# 그래프 표시
st.markdown(f'### KOSPI와 {", ".join(commodities)}의 장기 시계열 추이 ({start_date} - {end_date}, 정규화)')
plot_data(commodity_data_normalized, kospi_data_normalized, f'KOSPI and {", ".join(commodities)} Long-term Trend ({start_date} - {end_date}, Normalized)')

# 상관계수 계산 및 표시
for commodity in commodities:
    correlation = kospi_data_normalized.corr(commodity_data_normalized[commodity])
    st.markdown(f'### {commodity}와 KOSPI 간의 상관계수: {correlation:.2f}')
