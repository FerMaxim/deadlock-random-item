document.addEventListener('DOMContentLoaded', () => {
    let itemsDatabase = [];
    let currentCategoryPrice = 'all'; // 'all', '500', '1250', '3000', '6200'
    let isRolling = false;

    const rollButton = document.getElementById('rollButton');
    const categoryButtons = document.querySelectorAll('.button-group .btn');
    const itemShowcase = document.getElementById('itemShowcase');
    const historyList = document.getElementById('historyList');

    // 1. Fetch data
    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            itemsDatabase = data;
            console.log('Items loaded:', itemsDatabase.length);
        })
        .catch(err => {
            console.error('Failed to load items:', err);
            itemShowcase.innerHTML = `<div class="idle-state"><p style="color:red">Error loading item database.</p></div>`;
        });

    // 2. Category Selection
    categoryButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if(isRolling) return; // Prevent changing during animation
            
            // remove active class
            categoryButtons.forEach(b => b.classList.remove('active'));
            
            // add active to clicked
            const target = e.currentTarget;
            target.classList.add('active');
            
            // update state
            currentCategoryPrice = target.dataset.price;
        });
    });

    // 3. Roll Logic
    rollButton.addEventListener('click', () => {
        if (isRolling || itemsDatabase.length === 0) return;
        
        // Filter items
        let pool = [];
        if (currentCategoryPrice === 'all') {
            pool = itemsDatabase;
        } else {
            const targetPrice = parseInt(currentCategoryPrice);
            pool = itemsDatabase.filter(item => item.price === targetPrice);
        }

        if (pool.length === 0) {
            alert('No items found for this category.');
            return;
        }

        startRollAnimation(pool);
    });

    function startRollAnimation(pool) {
        isRolling = true;
        rollButton.style.opacity = '0.5';
        rollButton.style.cursor = 'not-allowed';
        rollButton.querySelector('.roll-text').innerText = "CALCULATING...";
        
        // Start visual rolling effect
        itemShowcase.classList.add('is-rolling');
        
        // Rapidly change inner HTML to simulate slot machine
        let rollInterval = setInterval(() => {
            const randomTempItem = pool[Math.floor(Math.random() * pool.length)];
            renderShowcaseContent(randomTempItem, true);
        }, 100);

        // Stop after 2 seconds
        setTimeout(() => {
            clearInterval(rollInterval);
            itemShowcase.classList.remove('is-rolling');
            
            // Pick final winner
            const winner = pool[Math.floor(Math.random() * pool.length)];
            
            // Render winner
            renderShowcaseContent(winner, false);
            addToHistory(winner);
            
            // Reset button
            isRolling = false;
            rollButton.style.opacity = '1';
            rollButton.style.cursor = 'pointer';
            rollButton.querySelector('.roll-text').innerText = "INITIALIZE RANDOMIZER";
            
        }, 1500);
    }

    function renderShowcaseContent(item, isTemp) {
        // If temp, just show a blurrier fast version, or just minimal structure
        const animationClass = isTemp ? '' : 'item-card ' + item.category;
        
        itemShowcase.innerHTML = `
            <div class="${animationClass}" style="${isTemp ? 'opacity: 0.5; padding: 20px; width:100%; height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center;' : ''}">
                ${!isTemp ? `
                    <div class="item-name">${item.name}</div>
                    <img src="${item.image}" alt="${item.name}" class="item-image">
                    <div class="item-info">
                        <div class="item-meta">
                            <span class="item-price">${item.price}</span>
                            <span class="item-category">${item.category}</span>
                        </div>
                    </div>
                ` : `
                    <img src="${item.image}" alt="rolling" style="width:100px; height:100px; border-radius:50%; opacity:0.5; filter:blur(5px);">
                    <div style="margin-top:20px; font-family:var(--font-heading); font-size:1.5rem; color:white;">???</div>
                `}
            </div>
        `;
    }

    function addToHistory(item) {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <img src="${item.image}" alt="${item.name}">
            <span>${item.name}</span>
            <span style="color:var(--color-${item.category.toLowerCase()}); font-weight:bold; font-size:0.7rem;">${item.price}</span>
        `;
        
        historyList.prepend(historyItem);
        
        // keep max 10 items
        if(historyList.children.length > 10) {
            historyList.removeChild(historyList.lastChild);
        }
    }
});
