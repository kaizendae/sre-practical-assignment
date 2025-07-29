FROM node:22.10-slim
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install && npm install -g nodemon
COPY . .
EXPOSE 3000
CMD [ "nodemon", "--exec", "node", "--require", "./instrumentation.js", "index.js" ]
