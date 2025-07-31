FROM golang:1.24.5
RUN go install github.com/air-verse/air@latest
WORKDIR /app
COPY . .
EXPOSE 8080
ENTRYPOINT [ "air" ]
