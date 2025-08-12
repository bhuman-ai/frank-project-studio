// Frank Project Studio - Client App

class FrankStudio {
    constructor() {
        this.currentDoc = 'project';
        this.currentProject = null;
        this.messageContext = '';
        this.isConnected = false;
        this.projects = JSON.parse(localStorage.getItem('frankProjects') || '[]');
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadProjects();
        
        // Don't auto-connect until project selected
        // Auto-refresh docs every 10 seconds
        setInterval(() => {
            if (this.currentProject) {
                this.loadDoc(this.currentDoc);
            }
        }, 10000);
    }

    loadProjects() {
        const dropdown = document.getElementById('projectDropdown');
        
        // Clear existing options except first two
        while (dropdown.options.length > 2) {
            dropdown.remove(2);
        }
        
        // Add saved projects
        this.projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.url;
            option.textContent = project.name;
            dropdown.appendChild(option);
        });
        
        // Restore last selected project
        const lastProject = localStorage.getItem('lastProject');
        if (lastProject) {
            dropdown.value = lastProject;
            this.selectProject(lastProject);
        }
    }

    setupEventListeners() {
        // Project selector
        const dropdown = document.getElementById('projectDropdown');
        const urlInput = document.getElementById('projectUrl');
        const addBtn = document.getElementById('addProjectBtn');
        
        dropdown.addEventListener('change', (e) => {
            if (e.target.value === 'new') {
                // Show input field
                urlInput.classList.remove('hidden');
                addBtn.classList.remove('hidden');
                urlInput.focus();
            } else if (e.target.value) {
                // Select existing project
                urlInput.classList.add('hidden');
                addBtn.classList.add('hidden');
                this.selectProject(e.target.value);
            }
        });
        
        addBtn.addEventListener('click', () => this.addProject());
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addProject();
        });
        
        // Chat form
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Mobile tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });

        // Doc tabs
        document.querySelectorAll('.doc-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const docName = e.target.dataset.doc;
                this.switchDoc(docName);
            });
        });

        // Handle mobile keyboard
        const input = document.getElementById('messageInput');
        input.addEventListener('focus', () => {
            setTimeout(() => {
                input.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        });
    }
    
    async addProject() {
        const urlInput = document.getElementById('projectUrl');
        const url = urlInput.value.trim();
        
        if (!url || !url.includes('github.com')) {
            alert('Please enter a valid GitHub URL');
            return;
        }
        
        // Extract repo name
        const parts = url.split('/');
        const repoName = parts[parts.length - 1].replace('.git', '');
        const userName = parts[parts.length - 2];
        
        const project = {
            url: url,
            name: `${userName}/${repoName}`,
            added: new Date().toISOString()
        };
        
        // Save to localStorage
        this.projects.push(project);
        localStorage.setItem('frankProjects', JSON.stringify(this.projects));
        
        // Add to dropdown
        const dropdown = document.getElementById('projectDropdown');
        const option = document.createElement('option');
        option.value = url;
        option.textContent = project.name;
        dropdown.appendChild(option);
        
        // Select it
        dropdown.value = url;
        urlInput.value = '';
        urlInput.classList.add('hidden');
        document.getElementById('addProjectBtn').classList.add('hidden');
        
        // Initialize project
        this.selectProject(url);
    }
    
    async selectProject(url) {
        this.currentProject = url;
        localStorage.setItem('lastProject', url);
        
        const status = document.getElementById('status');
        status.textContent = 'Initializing project...';
        
        try {
            // Tell backend to switch/clone project
            const response = await fetch('/api/project', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ github_url: url })
            });
            
            const data = await response.json();
            
            if (data.success) {
                status.textContent = `${data.file_count} files | ${data.status}`;
                this.isConnected = true;
                this.checkConnection();
                this.loadDoc(this.currentDoc);
                
                // Show initial message
                this.addMessage(`Project loaded: ${data.name}. ${data.file_count} files analyzed. Let's build something great!`, 'system');
            } else {
                status.textContent = 'Failed to load project';
                this.addMessage('Error: ' + data.error, 'system');
            }
        } catch (error) {
            console.error('Project selection error:', error);
            status.textContent = 'Error loading project';
        }
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        event.target.classList.add('active');

        // Update panels
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        document.getElementById(tabName + 'Panel').classList.add('active');

        // Load docs if switching to docs tab
        if (tabName === 'docs') {
            this.loadDoc(this.currentDoc);
        }
    }

    switchDoc(docName) {
        // Update doc tabs
        document.querySelectorAll('.doc-tab').forEach(t => t.classList.remove('active'));
        event.target.classList.add('active');

        // Load new doc
        this.currentDoc = docName;
        this.loadDoc(docName);
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const message = input.value.trim();

        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        input.value = '';

        // Disable input
        input.disabled = true;
        sendBtn.disabled = true;

        // Show thinking
        const thinkingId = 'think-' + Date.now();
        this.addMessage('<span class="loading"></span>Frank is thinking...', 'system', thinkingId);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    context: this.messageContext
                })
            });

            const data = await response.json();

            // Remove thinking
            document.getElementById(thinkingId)?.remove();

            if (data.response) {
                this.addMessage(data.response, 'frank');

                // Update context
                this.messageContext += '\nUser: ' + message + '\nFrank: ' + data.response.substring(0, 200);
                if (this.messageContext.length > 2000) {
                    this.messageContext = this.messageContext.substring(this.messageContext.length - 2000);
                }

                // Check for doc updates
                if (data.doc_updates) {
                    this.showStatus('📝 Updating documents...');
                    setTimeout(() => this.loadDoc(this.currentDoc), 2000);
                }
            } else if (data.error) {
                this.addMessage('Error: ' + data.error, 'system');
            }

        } catch (error) {
            document.getElementById(thinkingId)?.remove();
            console.error('Send message error:', error);
            this.addMessage('Connection error. Make sure backend is running.', 'system');
        } finally {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }

    addMessage(text, type, id = null) {
        const messages = document.getElementById('messages');
        const message = document.createElement('div');
        message.className = 'message ' + type;
        message.innerHTML = text;
        if (id) message.id = id;
        messages.appendChild(message);

        // Smooth scroll
        setTimeout(() => {
            messages.scrollTop = messages.scrollHeight;
        }, 100);
    }

    async loadDoc(docName) {
        const docTitle = document.getElementById('docTitle');
        const docLines = document.getElementById('docLines');
        const docContent = document.getElementById('docContent');

        docTitle.textContent = docName + '.md';

        try {
            // Use get-docs endpoint
            const response = await fetch('/api/get-docs?doc=' + docName);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();

            if (data.content) {
                docContent.textContent = data.content;
                docLines.textContent = data.lines + ' lines';

                // Add update indicator if not demo
                if (!data.demo) {
                    const existingPulse = docLines.querySelector('.update-pulse');
                    if (!existingPulse) {
                        const pulse = document.createElement('span');
                        pulse.className = 'update-pulse';
                        docLines.appendChild(pulse);
                        setTimeout(() => pulse.remove(), 3000);
                    }
                }
            } else if (data.error) {
                docContent.textContent = 'Error loading document: ' + data.error;
            }
        } catch (error) {
            console.error('Load doc error:', error);
            docContent.textContent = `# ${docName}.md\n\nConnect backend to see live documents.`;
        }
    }

    async checkConnection() {
        const status = document.getElementById('status');

        try {
            const response = await fetch('/api/health');
            
            if (response.ok) {
                const data = await response.json();
                this.isConnected = true;
                status.textContent = data.status || 'Connected to Frank';
                this.showStatus('✅ Connected to backend');
            } else {
                this.isConnected = false;
                status.textContent = 'Backend offline';
                this.showStatus('⚠️ Backend not connected');
            }
        } catch (error) {
            this.isConnected = false;
            status.textContent = 'Connect your Codespace';
            console.log('Backend not connected - this is normal if running frontend only');
        }
    }

    showStatus(message) {
        const status = document.getElementById('connectionStatus');
        status.textContent = message;
        status.classList.add('show');

        setTimeout(() => {
            status.classList.remove('show');
        }, 3000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.frankStudio = new FrankStudio();
});