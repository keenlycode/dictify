const gulp = require('gulp');
const stylus = require('gulp-stylus');

function bits_ui() {
    return gulp.src('bits-ui/bits-ui.styl')
    .pipe(stylus())
    .pipe(gulp.dest('../docs/bits-ui/'));
};

function template_stylus() {
    return gulp.src('template/**/*.styl')
    .pipe(stylus())
    .pipe(gulp.dest('../docs/'));
};

exports.default = gulp.series(bits_ui, template_stylus);
