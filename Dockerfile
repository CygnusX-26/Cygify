FROM python:3.8-slim-buster

WORKDIR /app

#Setup Requirements
COPY . .
ENV TOKEN=${{ secrets.TOKEN }}
ENV SP_SECRET=${{ secrets.SP_SECRET }}
ENV SP_ID=${{ secrets.SP_ID }}
RUN pip3 install -r requirements.txt
CMD ["python3", "/app/discordBot.py"] 
