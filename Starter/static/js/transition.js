export default {
    theme: {
        extend: {
            keyframes: {
                'slide-left': {
                    from: { transform: 'translateX(0)' },
                    to: { transform: 'translateX(-100%)' },
                },
            },
            animation: {
                'slide-left': 'slide-left 8s linear infinite',
            },
        },
    },
    plugins: [],
};