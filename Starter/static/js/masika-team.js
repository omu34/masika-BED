function swipeCards() {
    return {
        cards: [
            {
                id: 1,
                image: 'static/images/masika.jpg',
                title: 'Alex Masika',
                description: 'Senior Partner.',
                price: 8.99,
                link: 'skmasika@gmail.com',
            },
            {
                id: 2,
                image: 'static/images/koross.jpg',
                title: 'Ann Koross',
                description: 'Now Jurist at ELC.',
                link: 'skmasika@gmail.com',
                // link: 'https://lqrs.com'
            },
            {
                id: 3,
                image: 'static/images/pius.jpg',
                title: 'Dr. Pius Wanjala',
                description: 'Partner.',
                // price: 4.99,
               link: 'skmasika@gmail.com'
            },
            {
                id: 4,
                image: 'static/images/nelson.jpg',
                title: 'Nelson Kuya',
                description: 'Legal Assistant.',
                // price: 7.99,
                link: 'skmasika@gmail.com'
            },
            {
                id: 5,
                image: 'static/images/tomas.jpg',
                title: 'Thomas Opunga',
                description: 'Associate Lawyer.',
                // price: 6.49,
               link: 'skmasika@gmail.com'
            },
            {
                id: 6,
                image: 'static/images/pius.jpg',
                title: 'Dr. Pius Wanjala',
                description: 'Partner.',
                // price: 3.99,
                link: 'skmasika@gmail.com'
            },
            {
                id: 7,
                image: 'static/images/nelson.jpg',
                title: 'Nelson Kuya',
                description: 'Legal Assistant.',
                // price: 3.99,
               link: 'skmasika@gmail.com'
            }
        ],
        addToCart(product) {
            // Implement your add to cart logic here
            console.log('Adding to cart:', product);
        }
    };
}
