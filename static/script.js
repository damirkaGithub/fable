document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    let currentCardIndex = 0;

    // Инициализация карточек
    function initCards() {
        cards.forEach((card, index) => {
            card.style.display = index === 0 ? 'block' : 'none';
            card.style.transform = 'translateX(0) rotate(0)';
            card.style.transition = 'transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.1), opacity 0.5s ease';
        });
    }

    initCards();

    // Обработка анимации и скрытия карточки
    function processCardAction(card, isLike) {
        // Устанавливаем направление анимации
        const translateX = isLike ? '200px' : '-200px';
        const rotateDeg = isLike ? '20deg' : '-20deg';

        // Применяем анимацию
        card.style.transform = `translateX(${translateX}) rotate(${rotateDeg})`;
        card.style.opacity = '0';

        // Через 300ms скрываем карточку и показываем следующую
        setTimeout(() => {
            card.style.display = 'none';
            card.style.opacity = '1';
            card.style.transform = 'translateX(0) rotate(0)';

            currentCardIndex++;
            if (currentCardIndex < cards.length) {
                cards[currentCardIndex].style.display = 'block';
            } else {
                alert('Вы просмотрели все места!');
            }
        }, 300);
    }

    // Обработчики для кнопок
    window.handleLike = function(placeId) {
        const card = document.querySelector(`.card[data-place-id="${placeId}"]`);
        fetch(`/like/${placeId}`, { method: 'POST' });
        processCardAction(card, true);
    };

    window.handleDislike = function(placeId) {
        const card = document.querySelector(`.card[data-place-id="${placeId}"]`);
        fetch(`/dislike/${placeId}`, { method: 'POST' });
        processCardAction(card, false);
    };

    // Обработчики для свайпов
    let isDragging = false;
    let startX, currentX;

    const handleStart = (clientX) => {
        isDragging = true;
        startX = clientX;
        currentX = 0;
        cards[currentCardIndex].style.transition = 'none';
    };

    const handleMove = (clientX) => {
        if (!isDragging || currentCardIndex >= cards.length) return;

        currentX = clientX - startX;
        const rotateDeg = currentX / 15;
        cards[currentCardIndex].style.transform = `translateX(${currentX}px) rotate(${rotateDeg}deg)`;
    };

    const handleEnd = () => {
        if (!isDragging || currentCardIndex >= cards.length) return;
        isDragging = false;

        const card = cards[currentCardIndex];
        card.style.transition = 'transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.1), opacity 0.5s ease';

        const threshold = 100;

        if (Math.abs(currentX) > threshold) {
            if (currentX > 0) {
                fetch(`/like/${card.dataset.placeId}`, { method: 'POST' });
                processCardAction(card, true);
            } else {
                fetch(`/dislike/${card.dataset.placeId}`, { method: 'POST' });
                processCardAction(card, false);
            }
        } else {
            card.style.transform = 'translateX(0) rotate(0)';
        }
    };

    // Назначаем обработчики событий
    cards.forEach(card => {
        card.addEventListener('mousedown', (e) => {
            handleStart(e.clientX);
        });

        card.addEventListener('touchstart', (e) => {
            handleStart(e.touches[0].clientX);
        });
    });

    document.addEventListener('mousemove', (e) => {
        handleMove(e.clientX);
    });

    document.addEventListener('touchmove', (e) => {
        handleMove(e.touches[0].clientX);
    });

    document.addEventListener('mouseup', handleEnd);
    document.addEventListener('touchend', handleEnd);
});