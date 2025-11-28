document.addEventListener('DOMContentLoaded', function() {
    initThemeToggle();
    initMainNavigation();
    
    const urlInput = document.getElementById('url-input');
    const analyseBtn = document.getElementById('analyse-btn');
    const loading = document.getElementById('loading');
    const tabMenu = document.getElementById('tab-menu');
    const overviewSummary = document.getElementById('overview-summary');
    const overviewPlaceholder = document.getElementById('overview-placeholder');
    const overviewStats = document.getElementById('overview-stats');
    const overviewQuickWins = document.getElementById('overview-quick-wins');
    const uxAiLoading = document.getElementById('ux-ai-loading');
    const uxAiOutput = document.getElementById('ux-ai-output');
    const seoAiLoading = document.getElementById('seo-ai-loading');
    const seoAiOutput = document.getElementById('seo-ai-output');
    const autoTestRunBtn = document.getElementById('auto-test-run');
    const autoTestLoading = document.getElementById('auto-test-loading');
    const autoTestOutput = document.getElementById('auto-test-output');
    const competitorRunBtn = document.getElementById('competitor-run');
    const competitorLoading = document.getElementById('competitor-ai-loading');
    const competitorOutput = document.getElementById('competitor-ai-output');
    const allTasksContainer = document.getElementById('all-tasks-container');
    
    const storageKey = 'ai-build-coach-tasks';
    const uxAiStorageKey = 'ai-build-coach-ux-tasks';
    const seoAiStorageKey = 'ai-build-coach-seo-tasks';
    const competitorStorageKey = 'ai-build-coach-competitor-tasks';
    
    let currentAnalysedUrl = '';
    let analysisData = {
        basic: null,
        ux: null,
        seo: null,
        autoTest: null,
        competitor: null
    };

    function initThemeToggle() {
        const themeToggleBtn = document.getElementById('theme-toggle-btn');
        const savedTheme = localStorage.getItem('ai-build-coach-theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('ai-build-coach-theme', newTheme);
            });
        }
    }

    function initMainNavigation() {
        const mainNavBtns = document.querySelectorAll('.main-nav-btn');
        
        mainNavBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.dataset.mainTab;
                
                document.querySelectorAll('.main-section').forEach(section => {
                    section.classList.remove('active');
                });
                document.getElementById(`main-${targetTab}`).classList.add('active');
                
                mainNavBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    function showFriendlyAlert(message, type = 'info') {
        const icons = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            error: '❌'
        };
        alert(`${icons[type]} ${message}`);
    }

    initTabNavigation();

    analyseBtn.addEventListener('click', async function() {
        const url = urlInput.value.trim();

        if (!url) {
            showFriendlyAlert('Oops! Please paste a website link first 🔗', 'warning');
            return;
        }

        analyseBtn.disabled = true;
        loading.classList.remove('hidden');
        tabMenu.classList.add('hidden');
        overviewSummary.classList.add('hidden');
        overviewPlaceholder.classList.remove('hidden');

        analysisData = { basic: null, ux: null, seo: null, autoTest: null, competitor: null };
        uxAiOutput.innerHTML = '';
        seoAiOutput.innerHTML = '';
        autoTestOutput.innerHTML = '';
        competitorOutput.innerHTML = '';
        allTasksContainer.innerHTML = '';

        try {
            const response = await fetch('/full-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();
            currentAnalysedUrl = url;
            
            if (data.success) {
                analysisData.basic = data.basic || null;
                analysisData.ux = data.ux || null;
                analysisData.seo = data.seo || null;
                analysisData.competitor = (data.competitor && data.competitor.data) ? data.competitor.data : null;
                
                if (analysisData.ux) {
                    renderUXAIResults(analysisData.ux);
                }
                if (analysisData.seo) {
                    renderSEOAIResults(analysisData.seo);
                }
                if (analysisData.competitor) {
                    renderCompetitorResults(analysisData.competitor);
                } else {
                    competitorOutput.innerHTML = '<p>No competitor analysis available. Click "Run Competitor AI" to analyze.</p>';
                }
                
                tabMenu.classList.remove('hidden');
                overviewPlaceholder.classList.add('hidden');
                overviewSummary.classList.remove('hidden');
                
                updateOverview();
                updateAllTasks();
            } else {
                throw new Error(data.error || 'Analysis failed');
            }

        } catch (error) {
            overviewStats.innerHTML = '<p class="error-message">Error: ' + error.message + '</p>';
            tabMenu.classList.remove('hidden');
            overviewPlaceholder.classList.add('hidden');
            overviewSummary.classList.remove('hidden');
        } finally {
            analyseBtn.disabled = false;
            loading.classList.add('hidden');
        }
    });

    function initTabNavigation() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const target = btn.dataset.tab;
                
                document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
                document.querySelector(`#tab-${target}`).classList.add('active');

                document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    function switchToTab(tabName) {
        document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
        document.querySelector(`#tab-${tabName}`).classList.add('active');
        document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
        document.querySelector(`.tab-btn[data-tab="${tabName}"]`).classList.add('active');
    }

    autoTestRunBtn.addEventListener('click', async function() {
        if (!currentAnalysedUrl) {
            showFriendlyAlert('First, check a website using the link above! 🔗', 'info');
            return;
        }

        autoTestRunBtn.disabled = true;
        autoTestLoading.classList.remove('hidden');
        autoTestOutput.innerHTML = '';

        try {
            const response = await fetch('/auto-test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: currentAnalysedUrl })
            });

            const data = await response.json();

            if (data.success !== false) {
                analysisData.autoTest = data;
                renderAutoTestResults(data);
                updateOverview();
                updateAllTasks();
            } else {
                autoTestOutput.innerHTML = '<p class="error-message">Test failed: ' + (data.error || data.status || 'Unknown error') + '</p>';
            }

        } catch (error) {
            autoTestOutput.innerHTML = '<p class="error-message">Error: ' + error.message + '</p>';
        } finally {
            autoTestRunBtn.disabled = false;
            autoTestLoading.classList.add('hidden');
        }
    });

    competitorRunBtn.addEventListener('click', async function() {
        if (!currentAnalysedUrl) {
            showFriendlyAlert('First, check a website using the link above! 🔗', 'info');
            return;
        }

        competitorRunBtn.disabled = true;
        competitorLoading.classList.remove('hidden');
        competitorOutput.innerHTML = '';

        try {
            const response = await fetch('/competitor-ai', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: currentAnalysedUrl })
            });

            const data = await response.json();

            if (data.success && data.competitor_data) {
                analysisData.competitor = data.competitor_data;
                renderCompetitorResults(data.competitor_data);
                updateOverview();
                updateAllTasks();
            } else {
                competitorOutput.innerHTML = '<p class="error-message">Unable to perform competitor analysis: ' + (data.error || 'Unknown error') + '</p>';
            }

        } catch (error) {
            competitorOutput.innerHTML = '<p class="error-message">Error: ' + error.message + '</p>';
        } finally {
            competitorRunBtn.disabled = false;
            competitorLoading.classList.add('hidden');
        }
    });

    function updateOverview() {
        let uxTaskCount = 0;
        let seoTaskCount = 0;
        let basicTaskCount = 0;
        let competitorTaskCount = 0;
        let totalIssues = 0;
        let seoScore = '-';

        if (analysisData.basic && analysisData.basic.tasks) {
            basicTaskCount = analysisData.basic.tasks.length;
        }
        if (analysisData.ux && analysisData.ux.ai_tasks) {
            uxTaskCount = analysisData.ux.ai_tasks.length;
        }
        if (analysisData.seo) {
            if (analysisData.seo.ai_tasks) {
                seoTaskCount = analysisData.seo.ai_tasks.length;
            }
            if (analysisData.seo.score !== undefined) {
                seoScore = analysisData.seo.score;
            }
            if (analysisData.seo.issues) {
                totalIssues += analysisData.seo.issues.length;
            }
        }
        if (analysisData.competitor && analysisData.competitor.ai_tasks) {
            competitorTaskCount = analysisData.competitor.ai_tasks.length;
        }

        const totalTasks = basicTaskCount + uxTaskCount + seoTaskCount + competitorTaskCount;

        overviewStats.innerHTML = `
            <div class="stat-card ux-stat">
                <div class="stat-value">${uxTaskCount}</div>
                <div class="stat-label">UX Tasks</div>
            </div>
            <div class="stat-card seo-stat">
                <div class="stat-value">${seoScore}</div>
                <div class="stat-label">SEO Score</div>
            </div>
            <div class="stat-card tasks-stat">
                <div class="stat-value">${totalTasks}</div>
                <div class="stat-label">Total Tasks</div>
            </div>
            <div class="stat-card issues-stat">
                <div class="stat-value">${totalIssues}</div>
                <div class="stat-label">Issues Found</div>
            </div>
        `;

        let quickWinsHtml = '<h3>Quick Wins</h3>';
        const quickWins = [];

        if (analysisData.ux && analysisData.ux.ai_tasks) {
            const highPriority = analysisData.ux.ai_tasks.filter(t => t.priority === 'high').slice(0, 2);
            highPriority.forEach(t => quickWins.push({ source: 'UX', text: t.task || t.issue }));
        }
        if (analysisData.seo && analysisData.seo.ai_tasks) {
            const highPriority = analysisData.seo.ai_tasks.filter(t => t.priority === 'high').slice(0, 2);
            highPriority.forEach(t => quickWins.push({ source: 'SEO', text: t.task || t.issue }));
        }

        if (quickWins.length > 0) {
            quickWinsHtml += quickWins.slice(0, 4).map(qw => `
                <div class="quick-win-item">
                    <div class="quick-win-icon">!</div>
                    <span><strong>${qw.source}:</strong> ${escapeHtml(qw.text)}</span>
                </div>
            `).join('');
        } else {
            quickWinsHtml += '<p>Run the full analysis to see quick wins.</p>';
        }

        overviewQuickWins.innerHTML = quickWinsHtml;
    }

    function updateAllTasks() {
        let html = '';

        if (analysisData.basic && analysisData.basic.tasks && analysisData.basic.tasks.length > 0) {
            html += `
                <div class="task-category basic-category">
                    <div class="task-category-header">
                        <h3>Basic Analysis Tasks</h3>
                        <span class="task-count-badge">${analysisData.basic.tasks.length}</span>
                    </div>
                    <div class="tasks-list">
                        ${renderTasksWithFixPrompt(analysisData.basic.tasks, 'basic')}
                    </div>
                </div>
            `;
        }

        if (analysisData.ux && analysisData.ux.ai_tasks && analysisData.ux.ai_tasks.length > 0) {
            html += `
                <div class="task-category ux-category">
                    <div class="task-category-header">
                        <h3>UX Improvement Tasks</h3>
                        <span class="task-count-badge">${analysisData.ux.ai_tasks.length}</span>
                    </div>
                    <div class="tasks-list">
                        ${renderTasksWithFixPrompt(analysisData.ux.ai_tasks, 'ux')}
                    </div>
                </div>
            `;
        }

        if (analysisData.seo && analysisData.seo.ai_tasks && analysisData.seo.ai_tasks.length > 0) {
            html += `
                <div class="task-category seo-category">
                    <div class="task-category-header">
                        <h3>SEO Improvement Tasks</h3>
                        <span class="task-count-badge">${analysisData.seo.ai_tasks.length}</span>
                    </div>
                    <div class="tasks-list">
                        ${renderTasksWithFixPrompt(analysisData.seo.ai_tasks, 'seo')}
                    </div>
                </div>
            `;
        }

        if (analysisData.competitor && analysisData.competitor.ai_tasks && analysisData.competitor.ai_tasks.length > 0) {
            html += `
                <div class="task-category competitor-category">
                    <div class="task-category-header">
                        <h3>Competitive Improvement Tasks</h3>
                        <span class="task-count-badge">${analysisData.competitor.ai_tasks.length}</span>
                    </div>
                    <div class="tasks-list">
                        ${renderTasksWithFixPrompt(analysisData.competitor.ai_tasks, 'competitor')}
                    </div>
                </div>
            `;
        }

        if (!html) {
            html = '<p>No tasks yet. Run the analysis to generate tasks.</p>';
        }

        allTasksContainer.innerHTML = html;
        attachFixPromptHandlers();
    }

    function renderTasksWithFixPrompt(tasks, category) {
        const taskState = loadTaskState(storageKey);
        let html = '';

        tasks.forEach((task, index) => {
            const taskId = `${category}-task-${index}`;
            const isDone = taskState[taskId] || false;
            const checkedAttr = isDone ? 'checked' : '';

            const issue = task.issue || task.message || '';
            const taskDesc = task.task || task.description || '';
            const priority = task.priority || 'medium';
            const element = task.element || '';

            const fixPrompt = generateFixPrompt(issue, taskDesc, element);

            html += `
                <div class="task-item ${isDone ? 'task-completed' : ''}">
                    <input 
                        type="checkbox" 
                        class="task-checkbox" 
                        data-task-id="${taskId}" 
                        data-storage-key="${storageKey}"
                        ${checkedAttr}
                    >
                    <div class="task-content">
                        <div class="task-main">
                            <strong>${escapeHtml(issue)}</strong>
                            <span class="priority-badge priority-${priority}">${priority}</span>
                            <p>${escapeHtml(taskDesc)}</p>
                            ${element ? `<small class="task-element">Location: ${escapeHtml(element)}</small>` : ''}
                        </div>
                        <button class="fix-prompt-btn" data-prompt="${escapeForAttr(fixPrompt)}">
                            Get Fix Prompt
                        </button>
                    </div>
                </div>
            `;
        });

        return html;
    }

    function generateFixPrompt(issue, task, element) {
        let prompt = `Fix this issue: ${issue}\n\n`;
        if (task) {
            prompt += `What to do: ${task}\n\n`;
        }
        if (element) {
            prompt += `Location: ${element}\n\n`;
        }
        prompt += `Please provide the updated code to fix this issue.`;
        return prompt;
    }

    function renderDetailedIssue(issue) {
        if (typeof issue === 'string') {
            return `<div class="detailed-issue"><p>${escapeHtml(issue)}</p></div>`;
        }
        
        const title = issue.title || 'Issue';
        const description = issue.description || '';
        const location = issue.location || '';
        const whyItMatters = issue.why_it_matters || '';
        const stepsToFix = issue.steps_to_fix || [];
        const codeFix = issue.code_fix || '';
        const filesToModify = issue.files_to_modify || [];
        const promptToFix = issue.prompt_to_apply_fix || '';
        
        let html = `
            <div class="detailed-issue">
                <div class="issue-header">
                    <h4 class="issue-title">${escapeHtml(title)}</h4>
                    ${location ? `<span class="issue-location">${escapeHtml(location)}</span>` : ''}
                </div>
                ${description ? `<p class="issue-description">${escapeHtml(description)}</p>` : ''}
                ${whyItMatters ? `<p class="issue-why"><strong>Why it matters:</strong> ${escapeHtml(whyItMatters)}</p>` : ''}
        `;
        
        if (stepsToFix.length > 0) {
            html += `
                <div class="issue-steps">
                    <strong>Steps to fix:</strong>
                    <ol>
                        ${stepsToFix.map(step => `<li>${escapeHtml(step)}</li>`).join('')}
                    </ol>
                </div>
            `;
        }
        
        if (codeFix) {
            const cleanCode = codeFix.replace(/^```\w*\n?/, '').replace(/\n?```$/, '');
            html += `
                <div class="issue-code">
                    <strong>Code fix:</strong>
                    <pre><code>${escapeHtml(cleanCode)}</code></pre>
                    <button class="copy-btn" onclick="copyCode(this)">Copy Code</button>
                </div>
            `;
        }
        
        if (filesToModify.length > 0) {
            html += `<p class="issue-files"><strong>Files:</strong> ${filesToModify.map(f => escapeHtml(f)).join(', ')}</p>`;
        }
        
        if (promptToFix) {
            html += `
                <button class="fix-prompt-btn" data-prompt="${escapeForAttr(promptToFix)}">
                    Get Fix Prompt
                </button>
            `;
        }
        
        html += `</div>`;
        return html;
    }

    function attachFixPromptHandlers() {
        document.querySelectorAll('.fix-prompt-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const prompt = this.getAttribute('data-prompt');
                showFixPromptModal(prompt);
            });
        });

        document.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const taskId = this.getAttribute('data-task-id');
                const key = this.getAttribute('data-storage-key') || storageKey;
                const isChecked = this.checked;
                saveTaskState(key, taskId, isChecked);
                
                const taskItem = this.closest('.task-item');
                if (isChecked) {
                    taskItem.classList.add('task-completed');
                } else {
                    taskItem.classList.remove('task-completed');
                }
            });
        });
    }

    function showFixPromptModal(prompt) {
        const existingModal = document.getElementById('fix-prompt-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = 'fix-prompt-modal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Copy This Prompt</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <pre class="fix-prompt-text">${escapeHtml(prompt)}</pre>
                    <button class="copy-prompt-btn">Copy to Clipboard</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
        modal.querySelector('.copy-prompt-btn').addEventListener('click', function() {
            navigator.clipboard.writeText(prompt).then(() => {
                this.textContent = 'Copied!';
                setTimeout(() => this.textContent = 'Copy to Clipboard', 2000);
            });
        });
    }

    function renderAutoTestResults(data) {
        let html = '';

        const status = data.status || 'Unknown';
        const responseTime = data.response_time_ms || 0;
        const statusCode = data.status_code || 0;
        const summary = data.summary || '';
        const statusClass = status === 'Healthy' || status === 'Working' ? 'status-good' : 
                           status === 'Needs attention' || status === 'Slow' ? 'status-warning' : 'status-error';

        html += `
            <div class="auto-test-status ${statusClass}">
                <h3>Status: ${escapeHtml(status)}</h3>
                <p class="response-time">Response Time: ${responseTime}ms | HTTP ${statusCode}</p>
                ${summary ? `<p class="status-summary">${escapeHtml(summary)}</p>` : ''}
            </div>
        `;

        const checksPassed = data.checks_passed || data.checks || [];
        if (checksPassed.length > 0) {
            html += `
                <div class="auto-test-checks">
                    <h4>Passed Checks</h4>
                    <ul class="checks-passed">
                        ${checksPassed.map(check => `<li class="check-pass">${escapeHtml(String(check))}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        const issues = data.issues || [];
        if (issues.length > 0) {
            html += `
                <div class="auto-test-issues">
                    <h4>Issues Found (${issues.length})</h4>
                    <div class="issues-detailed-list">
                        ${issues.map(issue => renderDetailedIssue(issue)).join('')}
                    </div>
                </div>
            `;
        }

        if (!checksPassed.length && !issues.length) {
            html += '<p class="success-message">All checks passed! Your website looks healthy.</p>';
        }

        autoTestOutput.innerHTML = html;
        attachFixPromptHandlers();
    }

    function renderUXAIResults(uxData) {
        let html = '';

        const summary = typeof uxData.summary === 'string' ? uxData.summary : 
                       (uxData.summary && uxData.summary.text) ? uxData.summary.text :
                       (uxData.ai_summary) ? uxData.ai_summary : '';

        if (summary) {
            html += `
                <div class="ux-ai-summary">
                    <h3>Summary</h3>
                    <p>${escapeHtml(summary)}</p>
                </div>
            `;
        }

        if (uxData.issues && uxData.issues.length > 0) {
            html += `
                <div class="ux-ai-issues">
                    <h3>UX Issues Found (${uxData.issues.length})</h3>
                    <div class="issues-detailed-list">
                        ${uxData.issues.map(issue => renderDetailedIssue(issue)).join('')}
                    </div>
                </div>
            `;
        }

        if (uxData.recommendations && uxData.recommendations.length > 0) {
            html += `
                <div class="ux-ai-recommendations">
                    <h3>Quick Recommendations</h3>
                    <ul>
                        ${uxData.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (uxData.exact_fixes && uxData.exact_fixes.length > 0) {
            html += `
                <div class="ux-ai-fixes">
                    <h3>Quick Fixes</h3>
                    <div class="fixes-list">
                        ${uxData.exact_fixes.map(fix => `
                            <div class="fix-item">
                                <div class="fix-header">
                                    <span class="fix-selector">${escapeHtml(fix.selector || '')}</span>
                                    <span class="fix-description">${escapeHtml(fix.fix || '')}</span>
                                </div>
                                ${fix.code ? `
                                <pre class="fix-code"><code>${escapeHtml(fix.code)}</code></pre>
                                <button class="copy-btn" onclick="copyCode(this)">Copy Code</button>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        if (uxData.fix_prompt) {
            html += `
                <div class="ux-ai-fix-prompt">
                    <h3>Full Fix Prompt</h3>
                    <div class="fix-prompt-box">
                        <pre>${escapeHtml(uxData.fix_prompt)}</pre>
                        <button class="copy-btn" onclick="copyPromptToClipboard(this)">Copy Full Prompt</button>
                    </div>
                </div>
            `;
        }

        uxAiOutput.innerHTML = html || '<p>No UX issues found.</p>';
        attachFixPromptHandlers();
    }

    function renderSEOAIResults(seoData) {
        let html = '';

        if (seoData.score !== undefined) {
            const scoreClass = seoData.score >= 80 ? 'good' : seoData.score >= 50 ? 'moderate' : 'poor';
            html += `
                <div class="seo-ai-score-section">
                    <div class="seo-ai-score ${scoreClass}">
                        <span class="score-number">${seoData.score}</span>
                        <span class="score-label">SEO Score</span>
                    </div>
                </div>
            `;
        }

        const summary = typeof seoData.summary === 'string' ? seoData.summary :
                       (seoData.seo_summary) ? seoData.seo_summary : '';

        if (summary) {
            html += `
                <div class="seo-ai-summary">
                    <h3>Summary</h3>
                    <p>${escapeHtml(summary)}</p>
                </div>
            `;
        }

        if (seoData.suggested_keywords && seoData.suggested_keywords.length > 0) {
            html += `
                <div class="seo-ai-keywords">
                    <h3>Suggested Keywords</h3>
                    <div class="keywords-list">
                        ${seoData.suggested_keywords.map(kw => `<span class="keyword-tag">${escapeHtml(kw)}</span>`).join('')}
                    </div>
                </div>
            `;
        }

        if (seoData.issues && seoData.issues.length > 0) {
            html += `
                <div class="seo-ai-issues">
                    <h3>SEO Issues Found (${seoData.issues.length})</h3>
                    <div class="issues-detailed-list">
                        ${seoData.issues.map(issue => renderDetailedIssue(issue)).join('')}
                    </div>
                </div>
            `;
        }

        if (seoData.recommendations && seoData.recommendations.length > 0) {
            html += `
                <div class="seo-ai-recommendations">
                    <h3>Quick Recommendations</h3>
                    <ul>
                        ${seoData.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (seoData.fix_prompt) {
            html += `
                <div class="seo-ai-fix-prompt">
                    <h3>Full Fix Prompt</h3>
                    <div class="fix-prompt-box">
                        <pre>${escapeHtml(seoData.fix_prompt)}</pre>
                        <button class="copy-btn" onclick="copyPromptToClipboard(this)">Copy Full Prompt</button>
                    </div>
                </div>
            `;
        }

        seoAiOutput.innerHTML = html || '<p>No SEO issues found.</p>';
        attachFixPromptHandlers();
    }

    function renderCompetitorResults(compData) {
        let html = '';

        const summary = typeof compData.summary === 'string' ? compData.summary : '';
        const category = compData.category_detected || '';

        if (summary || category) {
            html += `
                <div class="competitor-summary">
                    <h3>Strategic Assessment</h3>
                    ${category ? `<p class="category-badge">Category: <strong>${escapeHtml(category)}</strong></p>` : ''}
                    ${summary ? `<p>${escapeHtml(summary)}</p>` : ''}
                </div>
            `;
        }

        if (compData.competitors_analyzed && compData.competitors_analyzed.length > 0) {
            html += `
                <div class="competitor-list">
                    <h3>Competitors Analyzed (${compData.competitors_analyzed.length})</h3>
                    <div class="competitors-grid">
                        ${compData.competitors_analyzed.map(comp => `
                            <div class="competitor-card">
                                <div class="comp-header">
                                    <strong>${escapeHtml(comp.name || 'Competitor')}</strong>
                                    ${comp.url ? `<a href="${escapeHtml(comp.url)}" target="_blank" class="comp-link">Visit</a>` : ''}
                                </div>
                                ${comp.key_features && comp.key_features.length > 0 ? `
                                    <div class="comp-features">
                                        <span class="comp-label">Key Features:</span>
                                        <ul>${comp.key_features.slice(0, 3).map(f => `<li>${escapeHtml(f)}</li>`).join('')}</ul>
                                    </div>
                                ` : ''}
                                ${comp.what_to_copy && comp.what_to_copy.length > 0 ? `
                                    <div class="comp-copy">
                                        <span class="comp-label">What to Copy:</span>
                                        <ul>${comp.what_to_copy.slice(0, 2).map(f => `<li>${escapeHtml(f)}</li>`).join('')}</ul>
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        if (compData.feature_gaps && compData.feature_gaps.length > 0) {
            html += `
                <div class="feature-gaps">
                    <h3>Feature Gaps (${compData.feature_gaps.length})</h3>
                    <div class="issues-detailed-list">
                        ${compData.feature_gaps.map(gap => renderFeatureGap(gap)).join('')}
                    </div>
                </div>
            `;
        }

        if (compData.strengths && compData.strengths.length > 0) {
            html += `
                <div class="competitor-strengths">
                    <h3>Your Competitive Strengths</h3>
                    <ul class="strengths-list">
                        ${compData.strengths.slice(0, 4).map(item => `<li>${escapeHtml(item)}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (compData.weaknesses && compData.weaknesses.length > 0) {
            html += `
                <div class="competitor-weaknesses">
                    <h3>Areas to Improve</h3>
                    <ul class="weaknesses-list">
                        ${compData.weaknesses.slice(0, 4).map(item => `<li>${escapeHtml(item)}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (compData.business_opportunities && compData.business_opportunities.length > 0) {
            html += `
                <div class="business-opportunities">
                    <h3>Business Opportunities</h3>
                    <ul class="opportunities-list">
                        ${compData.business_opportunities.slice(0, 4).map(item => `<li>${escapeHtml(item)}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        if (compData.final_recommendations && compData.final_recommendations.length > 0) {
            html += `
                <div class="final-recommendations">
                    <h3>Top Priority Actions</h3>
                    <ol class="recommendations-list">
                        ${compData.final_recommendations.slice(0, 4).map(item => `<li>${escapeHtml(item)}</li>`).join('')}
                    </ol>
                </div>
            `;
        }

        if (compData.fix_prompt) {
            html += `
                <div class="competitor-fix-prompt">
                    <h3>Full Implementation Prompt</h3>
                    <div class="fix-prompt-box">
                        <pre>${escapeHtml(compData.fix_prompt)}</pre>
                        <button class="copy-btn" onclick="copyPromptToClipboard(this)">Copy Full Prompt</button>
                    </div>
                </div>
            `;
        }

        competitorOutput.innerHTML = html || '<p>No competitor analysis available.</p>';
        attachFixPromptHandlers();
    }

    function renderFeatureGap(gap) {
        const title = gap.title || gap.gap || 'Feature Gap';
        const description = gap.description || '';
        const competitors = gap.competitors_who_have_it || [];
        const priority = gap.priority || 'medium';
        const whyNeeded = gap.why_you_need_it || '';
        const stepsToFix = gap.steps_to_fix || [];
        const codeFix = gap.code_fix || '';
        const filesToModify = gap.files_to_modify || [];
        const promptToFix = gap.prompt_to_apply_fix || '';
        
        let html = `
            <div class="detailed-issue feature-gap-item">
                <div class="issue-header">
                    <h4 class="issue-title">${escapeHtml(title)}</h4>
                    <span class="priority-badge priority-${priority}">${priority}</span>
                </div>
                ${description ? `<p class="issue-description">${escapeHtml(description)}</p>` : ''}
                ${competitors.length > 0 ? `
                    <p class="gap-competitors"><strong>Competitors with this:</strong> ${competitors.slice(0, 3).map(c => escapeHtml(c)).join(', ')}</p>
                ` : ''}
                ${whyNeeded ? `<p class="issue-why"><strong>Why you need it:</strong> ${escapeHtml(whyNeeded)}</p>` : ''}
        `;
        
        if (stepsToFix.length > 0) {
            html += `
                <div class="issue-steps">
                    <strong>How to add it:</strong>
                    <ol>
                        ${stepsToFix.map(step => `<li>${escapeHtml(step)}</li>`).join('')}
                    </ol>
                </div>
            `;
        }
        
        if (codeFix) {
            const cleanCode = codeFix.replace(/^```\w*\n?/, '').replace(/\n?```$/, '');
            html += `
                <div class="issue-code">
                    <strong>Code example:</strong>
                    <pre><code>${escapeHtml(cleanCode)}</code></pre>
                    <button class="copy-btn" onclick="copyCode(this)">Copy Code</button>
                </div>
            `;
        }
        
        if (filesToModify.length > 0) {
            html += `<p class="issue-files"><strong>Files to modify:</strong> ${filesToModify.map(f => escapeHtml(f)).join(', ')}</p>`;
        }
        
        if (promptToFix) {
            html += `
                <button class="fix-prompt-btn" data-prompt="${escapeForAttr(promptToFix)}">
                    Get Implementation Prompt
                </button>
            `;
        }
        
        html += `</div>`;
        return html;
    }

    function loadTaskState(key) {
        try {
            const saved = localStorage.getItem(key);
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            return {};
        }
    }

    function saveTaskState(key, taskId, isChecked) {
        try {
            const state = loadTaskState(key);
            state[taskId] = isChecked;
            localStorage.setItem(key, JSON.stringify(state));
        } catch (e) {
            console.error('Failed to save task state:', e);
        }
    }

    function escapeHtml(text) {
        if (!text) return '';
        const str = String(text);
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function escapeForAttr(text) {
        if (!text) return '';
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '&#10;');
    }

    window.copyCode = function(btn) {
        const code = btn.previousElementSibling.textContent;
        navigator.clipboard.writeText(code).then(() => {
            btn.textContent = 'Copied!';
            setTimeout(() => btn.textContent = 'Copy Code', 2000);
        });
    };

    window.copyPromptToClipboard = function(btn) {
        const pre = btn.previousElementSibling;
        const text = pre.textContent;
        navigator.clipboard.writeText(text).then(() => {
            btn.textContent = 'Copied!';
            setTimeout(() => btn.textContent = 'Copy Full Prompt', 2000);
        });
    };

    window.copyToClipboard = function(btn, text) {
        navigator.clipboard.writeText(text).then(() => {
            btn.textContent = 'Copied!';
            setTimeout(() => btn.textContent = 'Copy Code', 2000);
        });
    };

    // ============================================
    // BUILD FLOW FUNCTIONALITY
    // ============================================
    
    const ideaInput = document.getElementById('idea-input');
    const generateWorkflowBtn = document.getElementById('generate-workflow-btn');
    const workflowLoading = document.getElementById('workflow-loading');
    const workflowOutput = document.getElementById('workflow-output');
    const workflowSummary = document.getElementById('workflow-summary');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const testingBanner = document.getElementById('testing-banner');
    const priorityASteps = document.getElementById('priority-a-steps');
    const priorityBSteps = document.getElementById('priority-b-steps');
    const priorityCSteps = document.getElementById('priority-c-steps');
    const errorInput = document.getElementById('error-input');
    const fixErrorBtn = document.getElementById('fix-error-btn');
    const errorFixOutput = document.getElementById('error-fix-output');
    const copyAllPromptsBtn = document.getElementById('copy-all-prompts-btn');
    const copyBuildPlanBtn = document.getElementById('copy-build-plan-btn');
    
    let currentWorkflow = null;
    let currentPrompts = {};
    const workflowStorageKey = 'ai-build-coach-workflow';
    
    if (copyAllPromptsBtn) {
        copyAllPromptsBtn.addEventListener('click', function() {
            if (!currentWorkflow) return;
            
            const steps = currentWorkflow.build_steps || currentWorkflow.steps || [];
            let allPrompts = [];
            
            steps.forEach((step, index) => {
                const prompt = step.replit_prompt || currentPrompts[String(step.id)] || '';
                if (prompt) {
                    allPrompts.push(`--- Step ${index + 1}: ${step.title || step.name} ---\n${prompt}`);
                }
            });
            
            const combinedPrompts = allPrompts.join('\n\n');
            
            navigator.clipboard.writeText(combinedPrompts).then(() => {
                copyAllPromptsBtn.innerHTML = '<span class="btn-icon">✅</span><span class="btn-text">Copied!</span>';
                setTimeout(() => {
                    copyAllPromptsBtn.innerHTML = '<span class="btn-icon">📋</span><span class="btn-text">Copy All Prompts</span>';
                }, 2000);
            });
        });
    }
    
    if (copyBuildPlanBtn) {
        copyBuildPlanBtn.addEventListener('click', function() {
            if (!currentWorkflow) return;
            
            const summary = currentWorkflow.summary || 'Build Plan';
            const techStack = currentWorkflow.tech_stack || {};
            const steps = currentWorkflow.build_steps || currentWorkflow.steps || [];
            
            let planText = `# ${summary}\n\n`;
            
            if (Object.keys(techStack).length > 0) {
                planText += `## Tech Stack\n`;
                if (techStack.frontend) planText += `- Frontend: ${techStack.frontend}\n`;
                if (techStack.backend) planText += `- Backend: ${techStack.backend}\n`;
                if (techStack.database) planText += `- Database: ${techStack.database}\n`;
                planText += '\n';
            }
            
            planText += `## Build Steps\n\n`;
            
            const grouped = { A: [], B: [], C: [] };
            steps.forEach(step => {
                const priority = step.priority || 'B';
                if (grouped[priority]) grouped[priority].push(step);
            });
            
            if (grouped.A.length > 0) {
                planText += `### Priority A - Must Have (Core)\n`;
                grouped.A.forEach((step, i) => {
                    planText += `${i + 1}. **${step.title || step.name}**\n`;
                    if (step.what_this_step_is) planText += `   ${step.what_this_step_is}\n`;
                    planText += '\n';
                });
            }
            
            if (grouped.B.length > 0) {
                planText += `### Priority B - Should Have (Features)\n`;
                grouped.B.forEach((step, i) => {
                    planText += `${i + 1}. **${step.title || step.name}**\n`;
                    if (step.what_this_step_is) planText += `   ${step.what_this_step_is}\n`;
                    planText += '\n';
                });
            }
            
            if (grouped.C.length > 0) {
                planText += `### Priority C - Nice to Have (Extras)\n`;
                grouped.C.forEach((step, i) => {
                    planText += `${i + 1}. **${step.title || step.name}**\n`;
                    if (step.what_this_step_is) planText += `   ${step.what_this_step_is}\n`;
                    planText += '\n';
                });
            }
            
            navigator.clipboard.writeText(planText).then(() => {
                copyBuildPlanBtn.innerHTML = '<span class="btn-icon">✅</span><span class="btn-text">Copied!</span>';
                setTimeout(() => {
                    copyBuildPlanBtn.innerHTML = '<span class="btn-icon">📄</span><span class="btn-text">Copy Build Plan</span>';
                }, 2000);
            });
        });
    }
    
    if (generateWorkflowBtn) {
        generateWorkflowBtn.addEventListener('click', async function() {
            const idea = ideaInput.value.trim();
            
            if (!idea) {
                showFriendlyAlert('Tell me what you want to build! ✨', 'info');
                return;
            }
            
            generateWorkflowBtn.disabled = true;
            workflowLoading.classList.remove('hidden');
            workflowOutput.classList.add('hidden');
            
            try {
                const response = await fetch('/workflow', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ idea: idea })
                });
                
                const data = await response.json();
                
                if (data.success && data.workflow) {
                    currentWorkflow = data.workflow;
                    currentPrompts = data.prompts || {};
                    saveWorkflowState();
                    renderWorkflow();
                    workflowOutput.classList.remove('hidden');
                } else {
                    throw new Error(data.error || 'Failed to generate workflow');
                }
                
            } catch (error) {
                showFriendlyAlert('Oops! Something went wrong: ' + error.message, 'error');
            } finally {
                generateWorkflowBtn.disabled = false;
                workflowLoading.classList.add('hidden');
            }
        });
    }
    
    function renderWorkflow() {
        if (!currentWorkflow) return;
        
        const summary = currentWorkflow.app_summary || currentWorkflow.summary || 'Your app blueprint';
        const techStack = currentWorkflow.tech_stack || {};
        const phase = currentWorkflow.phase || {};
        const phases = currentWorkflow.phases || [];
        const phaseProgress = currentWorkflow.phase_progress || [];
        const directoryStructure = currentWorkflow.directory_structure || [];
        const userFlow = currentWorkflow.user_flow || [];
        const progressHint = currentWorkflow.progress_hint || '';
        
        let summaryHtml = `
            <div class="workflow-header">
                <h3>${phase.emoji || '🚀'} ${escapeHtml(summary)}</h3>
                <div class="phase-badge">
                    ${escapeHtml(phase.name || 'Building')}
                </div>
            </div>
            <p class="phase-encouragement">${escapeHtml(phase.encouragement || 'Keep going!')}</p>
            <div class="tech-stack">
                ${techStack.frontend ? `<span class="tech-badge">${escapeHtml(techStack.frontend)}</span>` : ''}
                ${techStack.backend ? `<span class="tech-badge">${escapeHtml(techStack.backend)}</span>` : ''}
                ${techStack.database ? `<span class="tech-badge">${escapeHtml(techStack.database)}</span>` : ''}
                ${techStack.ai && techStack.ai !== 'none' ? `<span class="tech-badge ai-badge">${escapeHtml(techStack.ai)}</span>` : ''}
            </div>
        `;
        
        if (phaseProgress.length > 0) {
            summaryHtml += `
                <div class="phases-progress">
                    <h4>Build Phases</h4>
                    <div class="phases-list">
                        ${phaseProgress.map(p => `
                            <div class="phase-item ${p.status}">
                                <span class="phase-id">${escapeHtml(p.id)}</span>
                                <span class="phase-name">${escapeHtml(p.name.replace(/Phase [A-G] – /, ''))}</span>
                                <span class="phase-progress-bar">
                                    <span class="phase-progress-fill" style="width: ${p.percent}%"></span>
                                </span>
                                <span class="phase-percent">${p.percent}%</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        if (directoryStructure.length > 0) {
            summaryHtml += `
                <details class="directory-structure">
                    <summary>Project Structure</summary>
                    <ul>${directoryStructure.slice(0, 10).map(d => `<li>${escapeHtml(d)}</li>`).join('')}</ul>
                </details>
            `;
        }
        
        if (userFlow.length > 0) {
            summaryHtml += `
                <details class="user-flow">
                    <summary>User Flow</summary>
                    <ol>${userFlow.slice(0, 8).map(f => `<li>${escapeHtml(f)}</li>`).join('')}</ol>
                </details>
            `;
        }
        
        if (progressHint) {
            summaryHtml += `<p class="progress-hint">${escapeHtml(progressHint)}</p>`;
        }
        
        workflowSummary.innerHTML = summaryHtml;
        
        const progress = currentWorkflow.progress || { percent: 0, completed: 0, total: 0 };
        progressFill.style.width = progress.percent + '%';
        progressText.textContent = `${progress.percent}% Complete (${progress.completed}/${progress.total} steps)`;
        
        if (!currentWorkflow.testing_unlocked) {
            testingBanner.classList.remove('hidden');
        } else {
            testingBanner.classList.add('hidden');
        }
        
        const grouped = currentWorkflow.grouped_steps || { A: [], B: [], C: [] };
        priorityASteps.innerHTML = renderMicroSteps(grouped.A || []);
        priorityBSteps.innerHTML = renderMicroSteps(grouped.B || []);
        priorityCSteps.innerHTML = renderMicroSteps(grouped.C || []);
        
        attachStepHandlers();
    }
    
    function renderMicroSteps(steps) {
        if (!steps || steps.length === 0) {
            return '<p class="no-steps">No tasks in this level</p>';
        }
        
        return steps.map(step => {
            const isCompleted = step.status === 'completed';
            const prompt = step.replit_prompt || currentPrompts[String(step.id)] || '';
            const title = step.title || step.name || 'Step';
            const whatIs = step.what_this_step_is || step.description || '';
            const whyMatters = step.why_it_matters || step.why_this_step_matters || '';
            const filesToEdit = step.files_to_edit || [];
            const microInstructions = step.micro_step_instructions || [];
            const validationChecks = step.validation_check || [];
            const area = step.area || step.category || step.type || 'feature';
            const category = area;
            
            let html = `
                <div class="micro-step-item ${isCompleted ? 'completed' : ''}" data-step-id="${step.id}">
                    <div class="step-header">
                        <input 
                            type="checkbox" 
                            class="step-checkbox" 
                            data-step-id="${step.id}"
                            ${isCompleted ? 'checked' : ''}
                        >
                        <div class="step-title-row">
                            <span class="step-number">${step.order || step.id}</span>
                            <h4 class="step-title">${escapeHtml(title)}</h4>
                            <span class="step-category cat-${category}">${escapeHtml(category)}</span>
                        </div>
                    </div>
                    
                    <div class="step-details">
                        ${whatIs ? `<p class="step-what">${escapeHtml(whatIs)}</p>` : ''}
                        ${whyMatters ? `<p class="step-why"><strong>Why this matters:</strong> ${escapeHtml(whyMatters)}</p>` : ''}
            `;
            
            if (filesToEdit.length > 0) {
                html += `
                    <div class="step-files">
                        <strong>Files to edit:</strong> 
                        ${filesToEdit.map(f => `<code>${escapeHtml(f)}</code>`).join(' ')}
                    </div>
                `;
            }
            
            if (microInstructions.length > 0) {
                html += `
                    <details class="micro-instructions">
                        <summary>Step-by-Step Instructions</summary>
                        <ol>
                            ${microInstructions.map(inst => `<li>${escapeHtml(inst)}</li>`).join('')}
                        </ol>
                    </details>
                `;
            }
            
            if (validationChecks.length > 0) {
                html += `
                    <details class="validation-checks">
                        <summary>How to Know You're Done</summary>
                        <ul class="check-list">
                            ${validationChecks.map(check => `<li>${escapeHtml(check)}</li>`).join('')}
                        </ul>
                    </details>
                `;
            }
            
            html += `
                        <div class="step-actions">
                            <button class="generate-prompt-btn primary-btn" data-step-id="${step.id}" data-prompt="${escapeForAttr(prompt)}">
                                Get Replit Prompt
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            return html;
        }).join('');
    }
    
    function renderSteps(steps) {
        return renderMicroSteps(steps);
    }
    
    function attachStepHandlers() {
        document.querySelectorAll('.step-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', async function() {
                const stepId = parseInt(this.getAttribute('data-step-id'));
                const isChecked = this.checked;
                const newStatus = isChecked ? 'completed' : 'pending';
                
                const stepItem = this.closest('.step-item');
                if (isChecked) {
                    stepItem.classList.add('completed');
                } else {
                    stepItem.classList.remove('completed');
                }
                
                if (currentWorkflow) {
                    const steps = currentWorkflow.steps || [];
                    for (let step of steps) {
                        if (step.id === stepId) {
                            step.status = newStatus;
                            break;
                        }
                    }
                    
                    updateProgress();
                    saveWorkflowState();
                }
            });
        });
        
        document.querySelectorAll('.generate-prompt-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const prompt = this.getAttribute('data-prompt');
                if (prompt) {
                    showFixPromptModal(prompt);
                } else {
                    const stepId = this.getAttribute('data-step-id');
                    generateStepPrompt(stepId);
                }
            });
        });
    }
    
    async function generateStepPrompt(stepId) {
        const step = currentWorkflow.steps.find(s => s.id === parseInt(stepId));
        if (!step) return;
        
        try {
            const response = await fetch('/generate-prompt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    step: step,
                    context: currentWorkflow.summary || ''
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.prompt) {
                currentPrompts[String(stepId)] = data.prompt;
                showFixPromptModal(data.prompt);
            } else {
                showFriendlyAlert('Couldn\'t create the prompt. Try again!', 'warning');
            }
        } catch (error) {
            showFriendlyAlert('Something went wrong: ' + error.message, 'error');
        }
    }
    
    function updateProgress() {
        if (!currentWorkflow) return;
        
        const steps = currentWorkflow.build_steps || currentWorkflow.steps || [];
        const total = steps.length;
        const completed = steps.filter(s => s.status === 'completed').length;
        const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
        
        currentWorkflow.progress = { total, completed, percent };
        currentWorkflow.testing_unlocked = percent >= 70;
        
        currentWorkflow.phase = determinePhase(percent);
        
        progressFill.style.width = percent + '%';
        progressText.textContent = `${percent}% Complete (${completed}/${total} steps)`;
        
        if (!currentWorkflow.testing_unlocked) {
            testingBanner.classList.remove('hidden');
        } else {
            testingBanner.classList.add('hidden');
        }
        
        const grouped = { A: [], B: [], C: [] };
        for (let step of steps) {
            const priority = step.priority || 'B';
            if (grouped[priority]) {
                grouped[priority].push(step);
            }
        }
        currentWorkflow.grouped_steps = grouped;
        
        currentWorkflow.build_steps = steps;
        currentWorkflow.steps = steps;
    }
    
    function determinePhase(percent) {
        if (percent < 30) {
            return {
                name: 'Foundation',
                number: 1,
                description: 'Setting up the basics',
                emoji: '🏗️',
                encouragement: 'Great start! Keep going!'
            };
        } else if (percent < 70) {
            return {
                name: 'Building',
                number: 2,
                description: 'Adding the main features',
                emoji: '🔨',
                encouragement: 'You\'re doing amazing!'
            };
        } else if (percent < 100) {
            return {
                name: 'Polish',
                number: 3,
                description: 'Almost done!',
                emoji: '✨',
                encouragement: 'So close!'
            };
        } else {
            return {
                name: 'Complete',
                number: 4,
                description: 'Ready to publish!',
                emoji: '🚀',
                encouragement: 'Congratulations!'
            };
        }
    }
    
    function saveWorkflowState() {
        try {
            localStorage.setItem(workflowStorageKey, JSON.stringify({
                workflow: currentWorkflow,
                prompts: currentPrompts,
                idea: ideaInput.value
            }));
        } catch (e) {
            console.error('Failed to save workflow state:', e);
        }
    }
    
    function loadWorkflowState() {
        try {
            const saved = localStorage.getItem(workflowStorageKey);
            if (saved) {
                const data = JSON.parse(saved);
                currentWorkflow = data.workflow;
                currentPrompts = data.prompts || {};
                if (data.idea) {
                    ideaInput.value = data.idea;
                }
                if (currentWorkflow) {
                    renderWorkflow();
                    workflowOutput.classList.remove('hidden');
                }
            }
        } catch (e) {
            console.error('Failed to load workflow state:', e);
        }
    }
    
    if (fixErrorBtn) {
        fixErrorBtn.addEventListener('click', async function() {
            const errorMessage = errorInput.value.trim();
            
            if (!errorMessage) {
                showFriendlyAlert('Paste your error message first! 📋', 'info');
                return;
            }
            
            fixErrorBtn.disabled = true;
            fixErrorBtn.textContent = 'Generating...';
            
            try {
                const response = await fetch('/fix-error', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        error_message: errorMessage,
                        context: currentWorkflow ? currentWorkflow.summary : ''
                    })
                });
                
                const data = await response.json();
                
                if (data.success && data.prompt) {
                    errorFixOutput.innerHTML = `
                        <pre>${escapeHtml(data.prompt)}</pre>
                        <button class="copy-btn" onclick="copyErrorPrompt(this)">Copy Fix Prompt</button>
                    `;
                    errorFixOutput.classList.remove('hidden');
                } else {
                    throw new Error(data.error || 'Failed to generate fix prompt');
                }
                
            } catch (error) {
                showFriendlyAlert('Oops! ' + error.message, 'error');
            } finally {
                fixErrorBtn.disabled = false;
                fixErrorBtn.innerHTML = '<span class="btn-icon">🩹</span><span class="btn-text">Get Fix</span>';
            }
        });
    }
    
    window.copyErrorPrompt = function(btn) {
        const pre = btn.previousElementSibling;
        const text = pre.textContent;
        navigator.clipboard.writeText(text).then(() => {
            btn.textContent = 'Copied!';
            setTimeout(() => btn.textContent = 'Copy Fix Prompt', 2000);
        });
    };
    
    loadWorkflowState();
});
