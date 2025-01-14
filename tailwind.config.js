module.exports = {
  content: [
    './api/templates/**/*.html', // Include Flask HTML templates
    './api/static/src/**/*.css', // Include your input CSS
    './api/static/js/**/*.js', // Include your input JSs'
  ],
  theme: {
    extend: {
      fontFamily: {
        'bellmt': ['Bell MT', 'serif'],
        'bellmt-italic': ['Bell MT Italic', 'serif'],
        'bellmt-bold': ['Bell MT Bold', 'serif']
      },
    },
  },
  plugins: [],
};


