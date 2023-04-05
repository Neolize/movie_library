module.exports = {
    devtool: 'source-map',
    entry: {
        filename: './static/rating_movies/js/script.js',
    },
    output: {
        path: __dirname + '/static/dist',
        filename: 'bundle.js',
    },
};
