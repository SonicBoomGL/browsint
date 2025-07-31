// Browsint Web Interface JavaScript

class BrowsintApp {
    constructor() {
        this.currentSection = 'home';
        this.activeTasks = new Map();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkStatus();
        this.showSection('home');
        
        // Auto-refresh status every 30 seconds
        setInterval(() => this.checkStatus(), 30000);
    }

    setupEventListeners() {
        // Form submissions
        document.getElementById('single-download-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSingleDownload(new FormData(e.target));
        });

        document.getElementById('crawl-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleCrawl(new FormData(e.target));
        });

        document.getElementById('page-analysis-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handlePageAnalysis(new FormData(e.target));
        });

        document.getElementById('osint-crawl-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleOsintCrawl(new FormData(e.target));
        });

        document.getElementById('domain-analysis-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleDomainAnalysis(new FormData(e.target));
        });

        document.getElementById('email-analysis-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleEmailAnalysis(new FormData(e.target));
        });

        document.getElementById('username-analysis-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleUsernameAnalysis(new FormData(e.target));
        });
    }

    async checkStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            const statusIndicator = document.getElementById('status-indicator');
            if (data.status === 'running') {
                statusIndicator.innerHTML = '<i class="bi bi-circle-fill text-success me-1"></i>Online';
                this.updateSystemStatus(data);
            } else {
                statusIndicator.innerHTML = '<i class="bi bi-circle-fill text-danger me-1"></i>Offline';
            }
        } catch (error) {
            console.error('Status check failed:', error);
            const statusIndicator = document.getElementById('status-indicator');
            statusIndicator.innerHTML = '<i class="bi bi-circle-fill text-danger me-1"></i>Offline';
        }
    }

    updateSystemStatus(data) {
        const systemStatus = document.getElementById('system-status');
        if (systemStatus) {
            systemStatus.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="bi bi-key me-2"></i>API Keys Configurate</h6>
                        <div class="d-flex flex-wrap gap-2">
                            ${data.api_keys_configured.map(key => 
                                `<span class="badge bg-success">${key}</span>`
                            ).join('')}
                            ${data.api_keys_configured.length === 0 ? 
                                '<span class="text-muted">Nessuna API key configurata</span>' : ''}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="bi bi-database me-2"></i>Database</h6>
                        <span class="badge ${data.databases_initialized ? 'bg-success' : 'bg-warning'}">
                            ${data.databases_initialized ? 'Inizializzati' : 'Non inizializzati'}
                        </span>
                    </div>
                </div>
            `;
        }
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.display = 'none';
        });

        // Show selected section
        const section = document.getElementById(`${sectionName}-section`);
        if (section) {
            section.style.display = 'block';
            this.currentSection = sectionName;

            // Load section-specific data
            switch (sectionName) {
                case 'profiles':
                    this.loadProfiles();
                    break;
                case 'database':
                    this.loadDatabaseInfo();
                    break;
                case 'api-keys':
                    this.loadApiKeys();
                    break;
            }
        }

        // Update active menu item
        document.querySelectorAll('.list-group-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeItem = document.querySelector(`[onclick="showSection('${sectionName}')"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    showLoading(text = 'Elaborazione in corso...', subtext = 'Attendere prego') {
        document.getElementById('loadingText').textContent = text;
        document.getElementById('loadingSubtext').textContent = subtext;
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
        return modal;
    }

    hideLoading(modal) {
        if (modal) {
            modal.hide();
        }
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastBody = toast.querySelector('.toast-body');
        const toastHeader = toast.querySelector('.toast-header');
        
        // Update icon based on type
        const iconMap = {
            'success': 'bi-check-circle',
            'error': 'bi-exclamation-triangle',
            'warning': 'bi-exclamation-triangle',
            'info': 'bi-info-circle'
        };
        
        const icon = toastHeader.querySelector('i');
        icon.className = `bi ${iconMap[type] || iconMap.info} me-2`;
        
        toastBody.textContent = message;
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    showResults(title, content, type = 'info') {
        const resultsSection = document.getElementById('results-section');
        const resultsContent = document.getElementById('results-content');
        
        resultsContent.innerHTML = `
            <div class="result-item result-${type}">
                <h6>${title}</h6>
                ${content}
            </div>
        `;
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideResults() {
        document.getElementById('results-section').style.display = 'none';
    }

    // API Methods
    async handleSingleDownload(formData) {
        const modal = this.showLoading('Download in corso...', 'Scaricamento della pagina');
        
        try {
            const response = await fetch('/api/download/single', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast(`Pagina scaricata con successo (${data.content_length} bytes)`, 'success');
                this.showResults('Download Completato', `
                    <p><strong>URL:</strong> ${data.url}</p>
                    <p><strong>Dimensione:</strong> ${data.content_length} bytes</p>
                    <p class="text-success"><i class="bi bi-check-circle me-2"></i>Download completato con successo</p>
                `);
            } else {
                this.showToast(`Errore durante il download: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Errore di rete: ${error.message}`, 'error');
        } finally {
            this.hideLoading(modal);
        }
    }

    async handleCrawl(formData) {
        const modal = this.showLoading('Avvio crawling...', 'Inizializzazione del crawler');
        
        try {
            const response = await fetch('/api/crawl/basic', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.task_id) {
                this.hideLoading(modal);
                this.showToast('Crawling avviato', 'success');
                this.monitorTask(data.task_id, 'Crawling Base');
            } else {
                this.showToast('Errore durante l\'avvio del crawling', 'error');
            }
        } catch (error) {
            this.showToast(`Errore di rete: ${error.message}`, 'error');
        } finally {
            this.hideLoading(modal);
        }
    }

    async handlePageAnalysis(formData) {
        const modal = this.showLoading('Analisi in corso...', 'Analizzando la struttura della pagina');
        
        try {
            const response = await fetch('/api/analyze/page', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast('Analisi completata', 'success');
                this.displayPageAnalysis(data);
            } else {
                this.showToast(`Errore durante l'analisi: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Errore di rete: ${error.message}`, 'error');
        } finally {
            this.hideLoading(modal);
        }
    }

    async handleOsintCrawl(formData) {
        const modal = this.showLoading('Avvio OSINT crawling...', 'Inizializzazione del crawler OSINT');
        
        try {
            const response = await fetch('/api/crawl/osint', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.task_id) {
                this.hideLoading(modal);
                this.showToast('OSINT Crawling avviato', 'success');
                this.monitorTask(data.task_id, 'OSINT Crawling');
            } else {
                this.showToast('Errore durante l\'avvio del crawling OSINT', 'error');
            }
        } catch (error) {
            this.showToast(`Errore di rete: ${error.message}`, 'error');
        } finally {
            this.hideLoading(modal);
        }
    }

    async handleDomainAnalysis(formData) {
        const modal = this.showLoading('Analisi dominio...', 'Raccolta dati OSINT per il dominio');
        
        try {
            const response = await fetch('/api/osint/domain', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.task_id) {
                this.hideLoading(modal);
                this.showToast('Analisi dominio avviata', 'success');
                this.monitorTask(data.task_id, 'Analisi Dominio');
            } else {
                this.showToast('Errore durante l\'avvio dell\'analisi', 'error');
            }
        } catch (error) {
            this.showToast(`Errore di rete: ${error.message}`, 'error');
        } finally {
            this.hideLoading(modal);
        }
    }

    async handleEmailAnalysis(formData) {
        const modal = this.showLoading('Analisi email...', 'Raccolta dati OSINT per l\'email');
        
        try {
            const response = await fetch('/api/osint/email', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.task_id) {
                this.hideLoading(modal);
                this.showToast('Analisi email avviata', 'success');
                this.monitorTask(data.task_id, 'Analisi Email');
            } else {
                this.showToast('Errore durante l\'avvio dell\'analisi', 'error');
            }
        } catch (error) {
            this.showToast(`Errore di rete: ${error.message}`, 'error');
        } finally {
            this.hideLoading(modal);
        }
    }

    async handleUsernameAnalysis(formData) {
        const modal = this.showLoading('Ricerca username...', 'Scansione profili social media');
        
        try {
            const response = await fetch('/api/osint/username', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.task_id) {
                this.hideLoading(modal);
                this.showToast('Ricerca username avviata', 'success');
                this.monitorTask(data.task_id, 'Ricerca Username');
            } else {
                this.showToast('Errore durante l\'avvio della ricerca', 'error');
            }
        } catch (error) {
            this.showToast(`Errore di rete: ${error.message}`, 'error');
        } finally {
            this.hideLoading(modal);
        }
    }

    async monitorTask(taskId, taskName) {
        const checkInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/tasks/${taskId}`);
                const data = await response.json();
                
                if (data.status === 'completed') {
                    clearInterval(checkInterval);
                    this.showToast(`${taskName} completato`, 'success');
                    this.displayTaskResults(data, taskName);
                } else if (data.status === 'error') {
                    clearInterval(checkInterval);
                    this.showToast(`${taskName} fallito: ${data.error}`, 'error');
                }
                // Continue monitoring if status is 'running'
            } catch (error) {
                clearInterval(checkInterval);
                this.showToast(`Errore monitoraggio task: ${error.message}`, 'error');
            }
        }, 2000);
        
        // Store interval for cleanup
        this.activeTasks.set(taskId, checkInterval);
    }

    displayTaskResults(data, taskName) {
        let content = '';
        
        switch (data.type) {
            case 'basic_crawl':
                content = this.formatCrawlResults(data.stats);
                break;
            case 'osint_crawl':
                content = this.formatOsintCrawlResults(data.stats);
                break;
            case 'domain_analysis':
                content = this.formatDomainAnalysis(data.profile);
                break;
            case 'email_analysis':
                content = this.formatEmailAnalysis(data.profile);
                break;
            case 'username_analysis':
                content = this.formatUsernameAnalysis(data.profile);
                break;
            default:
                content = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        
        this.showResults(taskName, content, 'success');
    }

    displayPageAnalysis(data) {
        const parsed = data.parsed_data;
        const osint = data.osint_data;
        
        let content = `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="bi bi-file-text me-2"></i>Informazioni Pagina</h6>
                    <p><strong>URL:</strong> ${data.url}</p>
                    <p><strong>Titolo:</strong> ${parsed.title || 'N/A'}</p>
                    <p><strong>Descrizione:</strong> ${parsed.description || 'N/A'}</p>
                    <p><strong>Lingua:</strong> ${parsed.lang || 'N/A'}</p>
                    <p><strong>Dimensione contenuto:</strong> ${parsed.content_length} bytes</p>
                </div>
                <div class="col-md-6">
                    <h6><i class="bi bi-link me-2"></i>Statistiche Link</h6>
                    <p><strong>Link totali:</strong> ${parsed.links?.length || 0}</p>
                    <p><strong>Link interni:</strong> ${parsed.internal_links_count || 0}</p>
                    <p><strong>Link esterni:</strong> ${parsed.external_links_count || 0}</p>
                    <p><strong>Immagini:</strong> ${parsed.image_count || 0}</p>
                    <p><strong>Script JS:</strong> ${parsed.js_count || 0}</p>
                    <p><strong>Fogli CSS:</strong> ${parsed.css_count || 0}</p>
                </div>
            </div>
        `;
        
        if (osint.emails && osint.emails.length > 0) {
            content += `
                <div class="mt-3">
                    <h6><i class="bi bi-envelope me-2"></i>Email trovate</h6>
                    <div class="d-flex flex-wrap gap-2">
                        ${osint.emails.map(email => `<span class="badge bg-info">${email}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        if (osint.phone_numbers && osint.phone_numbers.length > 0) {
            content += `
                <div class="mt-3">
                    <h6><i class="bi bi-telephone me-2"></i>Numeri di telefono trovati</h6>
                    <div class="d-flex flex-wrap gap-2">
                        ${osint.phone_numbers.map(phone => `<span class="badge bg-warning">${phone}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        if (osint.page_technologies) {
            content += `
                <div class="mt-3">
                    <h6><i class="bi bi-gear me-2"></i>Tecnologie rilevate</h6>
                    <div class="code-block">${JSON.stringify(osint.page_technologies, null, 2)}</div>
                </div>
            `;
        }
        
        this.showResults('Analisi Pagina Completata', content, 'success');
    }

    formatCrawlResults(stats) {
        return `
            <div class="row">
                <div class="col-md-4">
                    <div class="text-center">
                        <h4 class="text-primary">${stats.urls_visited || 0}</h4>
                        <small class="text-muted">URL Visitati</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <h4 class="text-success">${stats.pages_saved || 0}</h4>
                        <small class="text-muted">Pagine Salvate</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <h4 class="text-warning">${stats.errors || 0}</h4>
                        <small class="text-muted">Errori</small>
                    </div>
                </div>
            </div>
            ${stats.download_path ? `<p class="mt-3"><strong>Percorso:</strong> ${stats.download_path}</p>` : ''}
        `;
    }

    formatOsintCrawlResults(stats) {
        let content = this.formatCrawlResults(stats);
        
        if (stats.osint_summary) {
            const summary = stats.osint_summary;
            content += `
                <div class="mt-4">
                    <h6><i class="bi bi-search me-2"></i>Risultati OSINT</h6>
                    <p><strong>Entità profilate:</strong> ${summary.entities_profiled?.length || 0}</p>
                </div>
            `;
            
            if (summary.entities_profiled && summary.entities_profiled.length > 0) {
                content += '<div class="mt-3"><h6>Dettagli:</h6>';
                summary.entities_profiled.forEach(entity => {
                    content += `
                        <div class="border-start-primary ps-3 mb-2">
                            <strong>${entity.entity_type}:</strong> ${entity.entity}<br>
                            <small class="text-muted">Pagina: ${entity.page_url}</small>
                        </div>
                    `;
                });
                content += '</div>';
            }
        }
        
        return content;
    }

    formatDomainAnalysis(profile) {
        if (!profile || profile.error) {
            return `<div class="alert alert-warning">Errore nell'analisi: ${profile?.error || 'Dati non disponibili'}</div>`;
        }
        
        let content = '<div class="row">';
        
        // Entity info
        if (profile.entity) {
            content += `
                <div class="col-12 mb-3">
                    <h6><i class="bi bi-info-circle me-2"></i>Informazioni Entità</h6>
                    <p><strong>Nome:</strong> ${profile.entity.name}</p>
                    <p><strong>Tipo:</strong> ${profile.entity.type}</p>
                    <p><strong>Dominio:</strong> ${profile.entity.domain || 'N/A'}</p>
                </div>
            `;
        }
        
        // Profiles data
        if (profile.profiles && profile.profiles.domain && profile.profiles.domain.raw) {
            const raw = profile.profiles.domain.raw;
            
            if (raw.whois) {
                content += `
                    <div class="col-md-6 mb-3">
                        <h6><i class="bi bi-globe me-2"></i>WHOIS</h6>
                        <div class="code-block">${JSON.stringify(raw.whois, null, 2)}</div>
                    </div>
                `;
            }
            
            if (raw.dns) {
                content += `
                    <div class="col-md-6 mb-3">
                        <h6><i class="bi bi-dns me-2"></i>DNS</h6>
                        <div class="code-block">${JSON.stringify(raw.dns, null, 2)}</div>
                    </div>
                `;
            }
            
            if (raw.shodan) {
                content += `
                    <div class="col-12 mb-3">
                        <h6><i class="bi bi-shield me-2"></i>Shodan</h6>
                        <div class="code-block">${JSON.stringify(raw.shodan, null, 2)}</div>
                    </div>
                `;
            }
        }
        
        content += '</div>';
        return content;
    }

    formatEmailAnalysis(profile) {
        if (!profile || profile.error) {
            return `<div class="alert alert-warning">Errore nell'analisi: ${profile?.error || 'Dati non disponibili'}</div>`;
        }
        
        let content = '';
        
        if (profile.profiles && profile.profiles.email && profile.profiles.email.raw) {
            const raw = profile.profiles.email.raw;
            
            if (raw.hunterio) {
                content += `
                    <div class="mb-3">
                        <h6><i class="bi bi-search me-2"></i>Hunter.io</h6>
                        <div class="code-block">${JSON.stringify(raw.hunterio, null, 2)}</div>
                    </div>
                `;
            }
            
            if (raw.breaches) {
                content += `
                    <div class="mb-3">
                        <h6><i class="bi bi-shield-exclamation me-2"></i>Data Breaches</h6>
                        <div class="code-block">${JSON.stringify(raw.breaches, null, 2)}</div>
                    </div>
                `;
            }
        }
        
        return content || '<div class="alert alert-info">Nessun dato disponibile per questa email</div>';
    }

    formatUsernameAnalysis(profile) {
        if (!profile || profile.error) {
            return `<div class="alert alert-warning">Errore nell'analisi: ${profile?.error || 'Dati non disponibili'}</div>`;
        }
        
        let content = '';
        
        if (profile.profiles) {
            content += `
                <div class="mb-3">
                    <h6><i class="bi bi-person me-2"></i>Profili Social Trovati</h6>
                    <div class="row">
            `;
            
            Object.entries(profile.profiles).forEach(([platform, data]) => {
                if (data.exists) {
                    content += `
                        <div class="col-md-6 mb-2">
                            <div class="card">
                                <div class="card-body py-2">
                                    <h6 class="card-title mb-1">${platform}</h6>
                                    <a href="${data.url}" target="_blank" class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-box-arrow-up-right me-1"></i>Visita
                                    </a>
                                </div>
                            </div>
                        </div>
                    `;
                }
            });
            
            content += '</div></div>';
        }
        
        if (profile.summary) {
            content += `
                <div class="mb-3">
                    <h6><i class="bi bi-bar-chart me-2"></i>Riepilogo</h6>
                    <p><strong>Profili trovati:</strong> ${profile.summary.profiles_found || 0}</p>
                    ${profile.summary.report_file ? `<p><strong>Report file:</strong> ${profile.summary.report_file}</p>` : ''}
                </div>
            `;
        }
        
        return content || '<div class="alert alert-info">Nessun profilo social trovato</div>';
    }

    async loadProfiles() {
        const profilesList = document.getElementById('profiles-list');
        profilesList.innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"></div></div>';
        
        try {
            const response = await fetch('/api/profiles/osint');
            const data = await response.json();
            
            if (data.success && data.profiles.length > 0) {
                let html = '<div class="table-responsive"><table class="table table-hover"><thead><tr>';
                html += '<th>ID</th><th>Nome</th><th>Tipo</th><th>Dominio</th><th>Fonti</th><th>Data</th><th>Azioni</th>';
                html += '</tr></thead><tbody>';
                
                data.profiles.forEach(profile => {
                    html += `
                        <tr>
                            <td>${profile.id}</td>
                            <td>${profile.name}</td>
                            <td><span class="badge bg-secondary">${profile.type}</span></td>
                            <td>${profile.domain || 'N/A'}</td>
                            <td>${profile.profile_sources?.join(', ') || 'N/A'}</td>
                            <td>${new Date(profile.created_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary" onclick="app.viewProfile(${profile.id})">
                                    <i class="bi bi-eye me-1"></i>Visualizza
                                </button>
                                <div class="btn-group ms-1">
                                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                                        <i class="bi bi-download"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="/api/export/profile/${profile.id}/json">JSON</a></li>
                                        <li><a class="dropdown-item" href="/api/export/profile/${profile.id}/html">HTML</a></li>
                                    </ul>
                                </div>
                            </td>
                        </tr>
                    `;
                });
                
                html += '</tbody></table></div>';
                profilesList.innerHTML = html;
            } else {
                profilesList.innerHTML = '<div class="alert alert-info">Nessun profilo OSINT trovato</div>';
            }
        } catch (error) {
            profilesList.innerHTML = '<div class="alert alert-danger">Errore nel caricamento dei profili</div>';
        }
    }

    async viewProfile(profileId) {
        const modal = this.showLoading('Caricamento profilo...', 'Recupero dati dal database');
        
        try {
            const response = await fetch(`/api/profiles/osint/${profileId}`);
            const data = await response.json();
            
            if (data.success) {
                this.hideLoading(modal);
                this.showResults(`Profilo OSINT #${profileId}`, this.formatProfileView(data.profile), 'info');
            } else {
                this.showToast('Profilo non trovato', 'error');
            }
        } catch (error) {
            this.showToast(`Errore nel caricamento: ${error.message}`, 'error');
        } finally {
            this.hideLoading(modal);
        }
    }

    formatProfileView(profile) {
        return `
            <div class="row">
                <div class="col-12">
                    <div class="code-block">${JSON.stringify(profile, null, 2)}</div>
                </div>
            </div>
        `;
    }

    async loadDatabaseInfo() {
        const dbInfo = document.getElementById('database-info');
        dbInfo.innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"></div></div>';
        
        try {
            const response = await fetch('/api/database/info');
            const data = await response.json();
            
            if (data.success) {
                let html = '<div class="row">';
                
                Object.entries(data.databases).forEach(([dbName, info]) => {
                    html += `
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-header">
                                    <h6 class="mb-0"><i class="bi bi-database me-2"></i>${dbName.toUpperCase()}</h6>
                                </div>
                                <div class="card-body">
                                    <p><strong>Dimensione:</strong> ${info.size_mb.toFixed(2)} MB</p>
                                    <h6>Tabelle:</h6>
                                    <div class="table-responsive">
                                        <table class="table table-sm">
                                            <thead>
                                                <tr><th>Nome</th><th>Righe</th></tr>
                                            </thead>
                                            <tbody>
                                                ${info.tables.map(table => 
                                                    `<tr><td>${table.name}</td><td>${table.rows}</td></tr>`
                                                ).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
                dbInfo.innerHTML = html;
            } else {
                dbInfo.innerHTML = '<div class="alert alert-danger">Errore nel caricamento delle informazioni del database</div>';
            }
        } catch (error) {
            dbInfo.innerHTML = '<div class="alert alert-danger">Errore di rete nel caricamento delle informazioni</div>';
        }
    }

    async loadApiKeys() {
        const apiKeysList = document.getElementById('api-keys-list');
        apiKeysList.innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"></div></div>';
        
        try {
            const response = await fetch('/api/keys');
            const data = await response.json();
            
            let html = `
                <div class="row">
                    <div class="col-12 mb-3">
                        <h6><i class="bi bi-key me-2"></i>API Keys Configurate</h6>
                    </div>
                </div>
                <div class="row">
            `;
            
            const services = ['hunterio', 'hibp', 'shodan', 'whoisxml', 'virustotal', 'securitytrails'];
            
            services.forEach(service => {
                const isConfigured = data.api_keys[service];
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="mb-1">${service.toUpperCase()}</h6>
                                        <small class="text-muted">
                                            ${isConfigured ? `Configurata: ${isConfigured}` : 'Non configurata'}
                                        </small>
                                    </div>
                                    <div>
                                        <span class="badge ${isConfigured ? 'bg-success' : 'bg-warning'}">
                                            ${isConfigured ? 'OK' : 'Mancante'}
                                        </span>
                                    </div>
                                </div>
                                <div class="mt-2">
                                    <button class="btn btn-sm btn-outline-primary" onclick="app.showApiKeyForm('${service}')">
                                        <i class="bi bi-pencil me-1"></i>Configura
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            apiKeysList.innerHTML = html;
        } catch (error) {
            apiKeysList.innerHTML = '<div class="alert alert-danger">Errore nel caricamento delle API keys</div>';
        }
    }

    showApiKeyForm(service) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Configura API Key - ${service.toUpperCase()}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="api-key-form">
                        <div class="modal-body">
                            <div class="mb-3">
                                <label class="form-label">API Key</label>
                                <input type="password" class="form-control" name="api_key" required>
                                <div class="form-text">Inserisci la tua API key per ${service}</div>
                            </div>
                            <input type="hidden" name="service" value="${service}">
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annulla</button>
                            <button type="submit" class="btn btn-primary">Salva</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.querySelector('#api-key-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            try {
                const response = await fetch('/api/keys', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.showToast(data.message, 'success');
                    bsModal.hide();
                    this.loadApiKeys(); // Reload the keys list
                } else {
                    this.showToast(`Errore: ${data.error}`, 'error');
                }
            } catch (error) {
                this.showToast(`Errore di rete: ${error.message}`, 'error');
            }
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
}

// Global functions for onclick handlers
function showSection(sectionName) {
    app.showSection(sectionName);
}

function hideResults() {
    app.hideResults();
}

function loadProfiles() {
    app.loadProfiles();
}

function loadDatabaseInfo() {
    app.loadDatabaseInfo();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BrowsintApp();
});