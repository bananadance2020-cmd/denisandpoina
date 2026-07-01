import re

with open("index.html", "r") as f:
    html = f.read()

# Clear out any old scripts
html = re.sub(r"<script>\s*setInterval\(\(\) => \{\s*try \{.*?</script>", "", html, flags=re.DOTALL)

new_script = """
<script>
setInterval(() => {
  try {
    const allEls = Array.from(document.querySelectorAll("*"));
    let wishesNode = null;
    let quizNode = null;
    
    for (let el of allEls) {
      let txt = (el.textContent || "").toUpperCase().trim();
      if (txt === "НАШИ ТЁПЛЫЕ ПОЖЕЛАНИЯ" || txt === "ТЁПЛЫЕ ПОЖЕЛАНИЯ") {
         wishesNode = el;
      }
      if (txt === "ОТПРАВИТЬ") {
         quizNode = el;
      }
    }
    
    // UI Layout Logic
    if (wishesNode && quizNode) {
        let wBlock = wishesNode;
        while (wBlock.parentElement && wBlock.parentElement.tagName !== "MAIN" && wBlock.parentElement.id !== "__next") {
            wBlock = wBlock.parentElement;
        }
        
        let qBlock = quizNode;
        while (qBlock.parentElement && qBlock.parentElement.tagName !== "MAIN" && qBlock.parentElement.id !== "__next") {
            qBlock = qBlock.parentElement;
        }
        
        if (wBlock !== qBlock && qBlock.previousElementSibling !== wBlock) {
             qBlock.parentElement.insertBefore(wBlock, qBlock);
        }
        
        let next = qBlock.nextElementSibling;
        while (next && next.textContent.trim().length < 50 && !next.textContent.toUpperCase().includes("БУДЕМ РАДЫ") && !next.textContent.toUpperCase().includes("ЖДЕМ")) {
            next.style.display = 'none';
            next = next.nextElementSibling;
        }
        
        let sections = document.querySelectorAll('section, main > div');
        for (let s of sections) {
            if (s.textContent.trim().length < 10) {
                s.style.display = 'none';
            }
        }
    }
    
    // VK FORM INTERCEPT LOGIC
    let submitBtn = Array.from(document.querySelectorAll('button, .btn')).find(el => el.textContent.trim().toUpperCase() === "ОТПРАВИТЬ");
    if (submitBtn && !submitBtn.dataset.vkBound) {
        submitBtn.dataset.vkBound = '1';
        
        submitBtn.addEventListener('click', () => {
            let formWrapper = submitBtn.closest('section') || submitBtn.closest('form') || document.body;
            let data = {};
            let inputs = formWrapper.querySelectorAll('input, textarea');
            
            for (let i of inputs) {
                // Check if it's a required field and it's empty - let native validation handle it first
                
                if (i.type === 'radio' || i.type === 'checkbox') {
                     if (i.checked) {
                         let labelText = "Опция";
                         if (i.labels && i.labels.length > 0) labelText = i.labels[0].textContent;
                         else if (i.nextElementSibling && (i.nextElementSibling.tagName === 'SPAN' || i.nextElementSibling.tagName === 'LABEL')) labelText = i.nextElementSibling.textContent;
                         else if (i.parentElement.textContent.trim()) labelText = i.parentElement.textContent;
                         
                         // Try to find the question title (usually an h3 or div above the inputs)
                         let group = i.closest('.radio-group') || i.closest('fieldset') || i.closest('div[role="group"]') || i.parentElement.parentElement;
                         let groupTitle = group.querySelector('h1, h2, h3, h4, .title, .question-title');
                         let category = i.name || (groupTitle ? groupTitle.textContent.trim() : "Выбор");
                         
                         if (!data[category]) data[category] = [];
                         data[category].push(labelText.trim().replace(i.value, '').trim()); 
                     }
                } else if (i.type !== 'hidden') {
                     let name = i.placeholder || i.name || "Поле";
                     if (i.value.trim() !== '') {
                         data[name] = i.value;
                     }
                }
            }
            
            // Format arrays
            let finalData = {};
            for (let k in data) {
                if (Array.isArray(data[k])) finalData[k] = data[k].join(", ");
                else finalData[k] = data[k];
            }
            
            // Send to our local proxy which forwards to VK
            fetch('/submit_form', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(finalData)
            });
        });
    }
    
  } catch (e) { }
}, 500);
</script>
"""

html = html.replace("</head>", new_script + "</head>")

with open("index.html", "w") as f:
    f.write(html)
