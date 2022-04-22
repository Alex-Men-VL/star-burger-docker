FROM node:16

WORKDIR /usr/src/app

COPY package.json package-lock.json ./
COPY bundles-src ./bundles-src

RUN npm ci --dev

RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
