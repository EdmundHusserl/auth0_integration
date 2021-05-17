FROM        node:14.15-slim
EXPOSE      4200
WORKDIR     /app
COPY        . .
RUN         npm update && npm install 
CMD         ["ng", "serve"]