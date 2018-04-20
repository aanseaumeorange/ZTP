const express = require('express');
const app = express();

app.use(express.static(__dirname));

app.get("/", function(req,res) {
	res.sendFile('index.html', {"root": __dirname});
});

app.listen(8080, () => {
	console.log('Server started!');
});
