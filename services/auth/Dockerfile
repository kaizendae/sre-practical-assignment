FROM golang:1.24.5
WORKDIR /app
COPY . .
RUN go build -o main .
EXPOSE 8080
CMD [ "/app/main" ]
