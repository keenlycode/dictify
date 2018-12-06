const gulp = require('gulp');
const stylus = require('gulp-stylus');
const md = require('gulp-markdown');

function bits_ui(cb) {
    gulp.src('bits-ui/bits-ui.styl')
    .pipe(stylus())
    .pipe(gulp.dest('../docs/static/bits-ui/'));
    cb();
};

function template_stylus(cb) {
    gulp.src('template/**/*.styl')
    .pipe(stylus())
    .pipe(gulp.dest('../docs/static/template/'));
    cb();
};

function asset(cb) {
    gulp.src('asset/**/*')
    .pipe(gulp.dest('../docs/static/asset/'))
    cb();
}

function lib(cb) {
    gulp.src('node_modules/bits-ui/dist/**/*')
    .pipe(gulp.dest('../docs/static/lib/bits-ui/'));

    return gulp.src('node_modules/prismjs/**/*')
    .pipe(gulp.dest('../docs/static/lib/prismjs/'))
}

function dev(cb) {
    default_();
    gulp.watch('template/**/*.styl', template_stylus)
    cb();
}

default_ = gulp.series(
    bits_ui,
    template_stylus,
    asset,
    lib
);

exports.default = default_;
exports.dev = dev;
