document.addEventListener('DOMContentLoaded', () => {
    let itemsDatabase = [];
    let currentCategoryPrice = 'all'; // Default
    let currentCategoryType = 'all'; // 'all', 'Weapon', 'Vitality', 'Spirit'
    let isRolling = false;
    let exhaustedItems = []; // Global history to prevent ANY repeats

    const rollButton = document.getElementById('rollButton');
    const priceButtons = document.querySelectorAll('.price-group .btn');
    const typeButtons = document.querySelectorAll('.type-group .btn');
    const itemShowcase = document.getElementById('itemShowcase');
    const historyList = document.getElementById('historyList');
    const newGameBtn = document.getElementById('newGameBtn');
    const shopContainer = document.getElementById('shopContent');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const shopCatButtons = document.querySelectorAll('.shop-cat-btn');

    let shopCategoryFilter = 'all';

    // 1. Fetch data
    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            itemsDatabase = data;
            console.log('Items loaded:', itemsDatabase.length);
            renderShop();
        })
        .catch(err => {
            console.error('Failed to load items:', err);
            itemShowcase.innerHTML = `<div class="idle-state"><p style="color:red">Error loading item database.</p></div>`;
        });

    // Tab Switching Logic
    tabButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            const targetId = e.currentTarget.dataset.target;
            e.currentTarget.classList.add('active');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // 2. Category Selection (Price)
    priceButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if(isRolling) return;
            priceButtons.forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            currentCategoryPrice = e.currentTarget.dataset.price;
        });
    });

    // Category Selection (Type)
    typeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if(isRolling) return;
            typeButtons.forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            currentCategoryType = e.currentTarget.dataset.type;
        });
    });

    // Shop Sidebar Selection
    shopCatButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            shopCatButtons.forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            shopCategoryFilter = e.currentTarget.dataset.cat;
            renderShop();
        });
    });

    // New Game Reset Logic
    if (newGameBtn) {
        newGameBtn.addEventListener('click', () => {
            if (isRolling) return;
            
            // Clear history and exhausted items
            exhaustedItems = [];
            historyList.innerHTML = '';
            
            // Reset showcase
            itemShowcase.innerHTML = `
                <div class="idle-state">
                    <div class="scanner-line"></div>
                    <p>AWAITING INPUT...</p>
                </div>
            `;
            
            // Re-render shop just in case
            renderShop();
        });
    }

    // 3. Roll Logic
    rollButton.addEventListener('click', () => {
        if (isRolling || itemsDatabase.length === 0) return;
        
        // Count how many active items we already have
        let activeCount = itemsDatabase.filter(i => exhaustedItems.includes(i.id) && i.isActive).length;
        const maxActiveReached = activeCount >= 4;
        
        // Filter items by price, type, and exclude exhausted ones
        let pool = itemsDatabase.filter(item => {
            const matchPrice = currentCategoryPrice === 'all' || item.price == currentCategoryPrice;
            const matchType = currentCategoryType === 'all' || item.category === currentCategoryType;
            const notExhausted = !exhaustedItems.includes(item.id);
            const activeLimitOk = !maxActiveReached || !item.isActive;
            return matchPrice && matchType && notExhausted && activeLimitOk;
        });

        if (pool.length === 0) {
            if (maxActiveReached) {
                alert('No items available! You have reached the maximum of 4 active items, and no passive items are left in this category.');
            } else {
                alert('Items in this category have run out! (No repeats rule)');
            }
            return;
        }

        startRollAnimation(pool);
    });

    function startRollAnimation(pool) {
        isRolling = true;
        rollButton.style.opacity = '0.5';
        rollButton.style.cursor = 'not-allowed';
        rollButton.querySelector('.roll-text').innerText = "CALCULATING...";
        
        itemShowcase.classList.add('is-rolling');
        
        let rollInterval = setInterval(() => {
            const randomTempItem = pool[Math.floor(Math.random() * pool.length)];
            renderShowcaseContent(randomTempItem, true);
        }, 30);

        setTimeout(() => {
            clearInterval(rollInterval);
            itemShowcase.classList.remove('is-rolling');
            
            // Pick final winner
            const winner = pool[Math.floor(Math.random() * pool.length)];
            exhaustedItems.push(winner.id); // Add to global no-repeat list
            
            // Render winner
            renderShowcaseContent(winner, false);
            addToHistory(winner);
            
            isRolling = false;
            rollButton.style.opacity = '1';
            rollButton.style.cursor = 'pointer';
            rollButton.querySelector('.roll-text').innerText = "INITIALIZE RANDOMIZER";
            
        }, 300);
    }

    function renderShowcaseContent(item, isTemp) {
        const animationClass = isTemp ? '' : 'item-card ' + item.category;
        
        itemShowcase.innerHTML = `
            <div class="${animationClass}" style="${isTemp ? 'opacity: 0.5; padding: 20px; width:100%; height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center;' : ''}">
                ${!isTemp ? `
                    <div class="item-name">${item.name}</div>
                    <img src="${item.image}" alt="${item.name}" class="item-image">
                    ${item.description ? `<div class="item-desc">${item.description}</div>` : ''}
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
        if (!historyList) return;
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <img src="${item.image}" alt="${item.name}">
            <span>${item.name}</span>
            <span style="color:var(--color-${item.category.toLowerCase()}); font-weight:bold; font-size:0.7rem;">${item.price}</span>
        `;
        
        historyList.prepend(historyItem);
        
        if(historyList.children.length > 15) {
            historyList.removeChild(historyList.lastChild);
        }
    }

    function renderShop() {
        if (!shopContainer) return;
        shopContainer.innerHTML = '';
        
        const tiers = [800, 1600, 3200, 6400];
        
        tiers.forEach((tier, index) => {
            const itemsInTier = itemsDatabase.filter(item => 
                item.price === tier && 
                (shopCategoryFilter === 'all' || item.category === shopCategoryFilter)
            );

            if (itemsInTier.length === 0) return;

            const tierBlock = document.createElement('div');
            tierBlock.className = 'shop-tier';
            
            let gridHtml = `<div class="shop-grid">`;
            
            itemsInTier.forEach(item => {
                gridHtml += `
                    <div class="shop-item ${item.category} has-tooltip">
                        <img src="${item.image}" alt="${item.name}" class="item-image" style="width:100%; border-radius:8px; margin-bottom:5px;">
                        <div class="item-name">${item.name}</div>
                        <div class="tooltip-content">
                            <strong style="color:var(--color-${item.category.toLowerCase()})">${item.name} (${item.price})</strong><br><br>
                            ${item.description}
                        </div>
                    </div>
                `;
            });
            
            gridHtml += `</div>`;
            
            tierBlock.innerHTML = `
                <h3>${tier} Tier ${index + 1}</h3>
                ${gridHtml}
            `;
            
            shopContainer.appendChild(tierBlock);
        });
    }

    // 4. Ability Randomizer Logic
    const generateBuildBtn = document.getElementById('generateBuildBtn');
    const abilityPathContainer = document.getElementById('abilityPath');

    if (generateBuildBtn) {
        generateBuildBtn.addEventListener('click', generateAbilityBuild);
    }

    function generateAbilityBuild() {
        generateBuildBtn.style.pointerEvents = 'none';
        generateBuildBtn.style.opacity = '0.5';
        
        // 4 abilities, each has 4 stages: 0=locked, 1=unlocked, 2=T1, 3=T2, 4=T3
        let abilities = [
            { name: 'Skill 1', stage: 0 },
            { name: 'Skill 2', stage: 0 },
            { name: 'Skill 3', stage: 0 },
            { name: 'Ultimate', stage: 0 }
        ];
        
        let path = [];
        let costMap = { 1: 0, 2: 1, 3: 2, 4: 5 }; // stage -> AP cost
        let labelMap = { 1: 'UNLOCK', 2: 'Tier 1', 3: 'Tier 2', 4: 'Tier 3' };
        let classMap = { 1: 'tier-unlock', 2: 'tier-1', 3: 'tier-2', 4: 'tier-3' };
        
        for (let i = 0; i < 16; i++) {
            // Find abilities that can still be upgraded (stage < 4)
            let available = abilities.filter(a => a.stage < 4);
            
            // Pick a random ability to upgrade
            let pick = available[Math.floor(Math.random() * available.length)];
            pick.stage++;
            
            path.push({
                name: pick.name,
                label: labelMap[pick.stage],
                cssClass: classMap[pick.stage],
                cost: costMap[pick.stage]
            });
        }
        
        // Render
        abilityPathContainer.innerHTML = '';
        
        path.forEach((step, index) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'path-step';
            stepDiv.style.animationDelay = `${index * 0.1}s`;
            
            stepDiv.innerHTML = `
                <div class="step-number">${index + 1}</div>
                <div class="step-details">
                    <span class="step-ability">${step.name}</span>
                    <span class="step-tier ${step.cssClass}">${step.label}</span>
                </div>
                <div class="step-cost" style="${step.cost === 0 ? 'color:#5ebd40;' : ''}">${step.cost} AP</div>
            `;
            
            abilityPathContainer.appendChild(stepDiv);
        });
        
        setTimeout(() => {
            generateBuildBtn.style.pointerEvents = 'auto';
            generateBuildBtn.style.opacity = '1';
        }, 1200);
    }
});
