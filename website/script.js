// Arabic letter values (1-29)
const letterValues = {
    'ء': 1, 'ا': 2, 'ب': 3, 'ت': 4, 'ث': 5,
    'ج': 6, 'ح': 7, 'خ': 8, 'د': 9, 'ذ': 10,
    'ر': 11, 'ز': 12, 'س': 13, 'ش': 14, 'ص': 15,
    'ض': 16, 'ط': 17, 'ظ': 18, 'ع': 19, 'غ': 20,
    'ف': 21, 'ق': 22, 'ك': 23, 'ل': 24, 'م': 25,
    'ن': 26, 'ه': 27, 'و': 28, 'ي': 29
};

// Functional letters (الحروف الزائدة العشرة)
const functionalLetters = ['س', 'ء', 'ل', 'ت', 'م', 'و', 'ن', 'ي', 'ه', 'ا'];

// Fibonacci layer values
const fibonacciLayers = {
    1: 3,   // Phonology
    2: 5,   // Morphology
    3: 8,   // Lexical
    4: 13,  // Syntax
    5: 21,  // Semantics
    6: 34   // Discourse
};

// Calculate root values and fractal relations
function calculateRoot() {
    const c1Input = document.getElementById('c1').value.trim();
    const c2Input = document.getElementById('c2').value.trim();
    const c3Input = document.getElementById('c3').value.trim();
    
    const resultsDiv = document.getElementById('results');
    
    // Validate inputs
    if (!c1Input || !c2Input || !c3Input) {
        resultsDiv.innerHTML = '<p style="color: #e74c3c;">الرجاء إدخال ثلاثة حروف</p>';
        return;
    }
    
    const v1 = letterValues[c1Input];
    const v2 = letterValues[c2Input];
    const v3 = letterValues[c3Input];
    
    if (!v1 || !v2 || !v3) {
        resultsDiv.innerHTML = '<p style="color: #e74c3c;">الرجاء إدخال حروف عربية صحيحة</p>';
        return;
    }
    
    // Calculate values
    const rootValue = v1 + v2 + v3;
    const rcb = v2 + v1;  // c + b (C1)
    const rca = v2 + v3;  // c + a (C2)
    const rba = v1 + v3;  // b + a (C3)
    const relationsSum = rcb + rca + rba;
    const c2Centrality = ((v2 / rootValue) * 100).toFixed(1);
    
    // Check if letters are functional
    const c1Functional = functionalLetters.includes(c1Input) ? '✓ وظيفي' : '';
    const c2Functional = functionalLetters.includes(c2Input) ? '✓ وظيفي' : '';
    const c3Functional = functionalLetters.includes(c3Input) ? '✓ وظيفي' : '';
    
    // Calculate word value with fatha (كَتَبَ pattern)
    const wordValueFatha = (v1 + 1) + (v2 + 1) + (v3 + 1);
    
    // Fractal layer values
    const morphologyValue = rootValue * fibonacciLayers[2];
    const semanticsValue = rootValue * fibonacciLayers[5];
    
    // Display results
    resultsDiv.innerHTML = `
        <div style="text-align: right; direction: rtl;">
            <h3 style="color: var(--gold); margin-bottom: 1rem;">نتائج الجذر: ${c1Input}-${c2Input}-${c3Input}</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <h4 style="color: var(--secondary-color);">قيم الحروف:</h4>
                    <p>${c1Input} (C1) = ${v1} ${c1Functional}</p>
                    <p>${c2Input} (C2) = ${v2} ${c2Functional}</p>
                    <p>${c3Input} (C3) = ${v3} ${c3Functional}</p>
                    <p><strong>قيمة الجذر = ${rootValue}</strong></p>
                </div>
                
                <div>
                    <h4 style="color: var(--secondary-color);">علاقات الفراكتال:</h4>
                    <p>rcb (C1→b) = ${rcb}</p>
                    <p>rca (C2→a) = ${rca}</p>
                    <p>rba (C3) = ${rba}</p>
                    <p><strong>المجموع = ${relationsSum}</strong></p>
                </div>
            </div>
            
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
                <p>✓ ${relationsSum} = 2 × ${rootValue} = ${2 * rootValue} ${relationsSum === 2 * rootValue ? '✓ صحيح!' : '✗'}</p>
                <p>مركزية C2: ${c2Centrality}%</p>
                <p>قيمة الكلمة بالفتحات: ${wordValueFatha}</p>
            </div>
            
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
                <h4 style="color: var(--secondary-color);">القيم الفراكتالية:</h4>
                <p>في طبقة الصرف (×5): ${morphologyValue}</p>
                <p>في طبقة الدلالة (×21): ${semanticsValue}</p>
            </div>
        </div>
    `;
}

// Smooth scrolling for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add enter key support for calculator
document.querySelectorAll('.root-inputs input').forEach(input => {
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            calculateRoot();
        }
    });
    
    // Auto-focus next input
    input.addEventListener('input', function() {
        if (this.value.length === 1) {
            const inputs = document.querySelectorAll('.root-inputs input');
            const currentIndex = Array.from(inputs).indexOf(this);
            if (currentIndex < inputs.length - 1) {
                inputs[currentIndex + 1].focus();
            }
        }
    });
});

// Animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.card, .layer-card, .file-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
});

// Console welcome message
console.log('%c AGT - المبرهنة العربية المولِّدة ', 
    'background: #1a1a2e; color: #d4af37; font-size: 20px; padding: 10px;');
console.log('Arabic Generative Theorem - Formal Verification Project');
console.log('Total Coq Lines: 4350+');
