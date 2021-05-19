FROM        node:14.15
EXPOSE      4200
WORKDIR     /app
COPY        . .
RUN         npm update && npm install 
CMD         ["npm", "start"]