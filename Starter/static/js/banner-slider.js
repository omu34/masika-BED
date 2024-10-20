document.addEventListener('alpine:init', () => {
    Alpine.data('slider', () => ({
        currentIndex: 0,
        images: [
            { 
                image: 'https://www.masikakoross.com/wp-content/uploads/2018/05/oie_LoZRjX2C0Svc.jpg', 
                captionImage: 'https://www.masikakoross.com/wp-content/themes/law-and-justice/css/../img/balance-icon-small.png',
                caption: ' Our team is dedicated to providing top-notch services', 
                // description: 'A world class professional legal firm geared to deliver excellence legal services to all'
            },           

            
            { 
                image: 'https://www.masikakoross.com/wp-content/uploads/2018/05/oie_YdLEhrPei1Va.jpg',
                captionImage: 'https://www.masikakoross.com/wp-content/themes/law-and-justice/css/../img/balance-icon-small.png',
               caption: 'YOU DESERVE THE BEST DEFENCE LAWYERS', 
                // description: 'We handle cases of all sizes.'
            },
            {
                image: 'https://mmsadvocates.co.ke/wp-content/uploads/2023/05/Nairobi-MMS.jpg',
                captionImage: 'https://www.masikakoross.com/wp-content/themes/law-and-justice/css/../img/balance-icon-small.png',
                caption: ' We handle residential property matters.',
                // description: 'A world class professional legal firm geared to deliver excellence legal services to all'
            },
            { 
                image: 'https://mmsadvocates.co.ke/wp-content/uploads/2023/05/Dispute-Resolution.jpg',
                captionImage: 'https://www.masikakoross.com/wp-content/themes/law-and-justice/css/../img/balance-icon-small.png',
               caption: 'WE HANDLE CASES OF ALL SIZES',
                // description: 'We handle cases of all sizes.'
            },
           
            { 
                image: ' https://mmsadvocates.co.ke/wp-content/uploads/2023/05/Dubai-MMS.jpg  ',
                captionImage: 'https://www.masikakoross.com/wp-content/themes/law-and-justice/css/../img/balance-icon-small.png',
               caption: 'Our firm provides legal services for commercial and corporate clients.', 
                // description: 'We handle cases of all sizes.'
            },            
            { 

                image: 'https://mmsadvocates.co.ke/wp-content/uploads/2023/05/Real-Estate.jpg',
                captionImage: 'https://www.masikakoross.com/wp-content/themes/law-and-justice/css/../img/balance-icon-small.png',
               caption: 'We provide legal representation for family law cases.', 
                // description: 'We handle cases of all sizes.'
            }
           
        ],
        interval: null,
        init() {
            this.startAutoSlide();
        },
        startAutoSlide() {
            this.interval = setInterval(() => {
                this.next();
            }, 10000); // 10s Adjust timing here as needed
        },
        back() {
            clearInterval(this.interval);
            this.currentIndex = (this.currentIndex - 0
                 + this.images.length) % this.images.length;
            this.startAutoSlide();
        },
        next() {
            clearInterval(this.interval);
            this.currentIndex = (this.currentIndex + 1) % this.images.length;
            this.startAutoSlide();
        }
    }))
});

