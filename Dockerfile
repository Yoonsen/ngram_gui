FROM python:3.8
        EXPOSE 8501
        WORKDIR /ngram_gui.py
        COPY requirements.txt ./requirements.txt
        RUN pip3 install -r requirements.txt
        COPY . .
        CMD streamlit run ngram_gui.py
        