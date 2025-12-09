document.addEventListener('DOMContentLoaded', () => {
    const journalEntryTextarea = document.getElementById('journalEntry');
    const addEntryBtn = document.getElementById('addEntryBtn');
    const journalEntriesDiv = document.getElementById('journalEntries');

    let entries = JSON.parse(localStorage.getItem('journalEntries')) || [];

    function saveEntries() {
        localStorage.setItem('journalEntries', JSON.stringify(entries));
    }

    function renderEntries() {
        journalEntriesDiv.innerHTML = ''; // Clear existing entries
        entries.forEach((entry, index) => {
            const entryDiv = document.createElement('div');
            entryDiv.classList.add('entry');
            entryDiv.innerHTML = `
                <div class="entry-date">${entry.date}</div>
                <div class="entry-content">${entry.content}</div>
            `;
            journalEntriesDiv.prepend(entryDiv); // Add new entries to the top
        });
    }

    addEntryBtn.addEventListener('click', () => {
        const content = journalEntryTextarea.value.trim();
        if (content) {
            const now = new Date();
            const dateOptions = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
            const formattedDate = now.toLocaleDateString('en-US', dateOptions);

            const newEntry = {
                date: formattedDate,
                content: content
            };
            entries.push(newEntry);
            saveEntries();
            renderEntries();
            journalEntryTextarea.value = ''; // Clear textarea
        } else {
            alert('Please write something before adding an entry.');
        }
    });

    // Initial render when the page loads
    renderEntries();
});

