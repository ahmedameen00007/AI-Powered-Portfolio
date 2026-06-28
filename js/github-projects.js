/**
 * github-projects.js
 * Automatically fetches and renders GitHub repositories into the portfolio.
 */

const GITHUB_USERNAME = 'ahmedameen00007';

// Mapping topics to category titles
const CATEGORY_MAP = {
    'computer-vision': 'Computer Vision',
    'cv': 'Computer Vision',
    'data-analysis': 'Data Analysis',
    'bi': 'Data Analysis',
    'machine-learning': 'Machine & Deep Learning',
    'deep-learning': 'Machine & Deep Learning',
    'ml': 'Machine & Deep Learning',
    'dl': 'Machine & Deep Learning',
    'generative-ai': 'Generative AI',
    'genai': 'Generative AI',
    'software': 'Software Development',
    'full-stack': 'Software Development'
};

async function fetchGithubRepos() {
    try {
        const response = await fetch(`https://api.github.com/users/${GITHUB_USERNAME}/repos?sort=updated&per_page=100`);
        if (!response.ok) throw new Error('GitHub API failed');
        const repos = await response.json();
        return repos.filter(repo => !repo.fork).sort((a, b) => b.stargazers_count - a.stargazers_count || new Date(b.updated_at) - new Date(a.updated_at));
    } catch (error) {
        console.error('Error fetching GitHub repos:', error);
        return null;
    }
}

function createProjectFeaturedHTML(repo) {
    const tags = repo.topics && repo.topics.length > 0 ? repo.topics.slice(0, 3) : ['GitHub', 'Portfolio', 'Project'];
    const description = repo.description || 'No description provided.';
    const topic = repo.topics && repo.topics[0] ? repo.topics[0].toUpperCase() : 'PROJECT';

    return `
        <a href="${repo.html_url}" target="_blank" class="project-featured glass animate-fade-up" style="text-decoration: none; color: inherit; display: block;">
            <div class="project-img-wrapper">
                <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, var(--color-primary-dark), var(--color-bg)); font-family: var(--font-display); font-size: 2rem; color: var(--color-primary); font-weight: 800; border-bottom: 1px solid var(--color-border);">
                    ${repo.name.substring(0, 15).toUpperCase()}
                </div>
            </div>
            <div class="project-details">
                <span class="project-category">${topic}</span>
                <h3 class="project-title-text">${repo.name}</h3>
                <p>${description}</p>
                <div class="project-tags">
                    ${tags.map(tag => `<span>${tag}</span>`).join('')}
                </div>
            </div>
        </a>
    `;
}

function createProjectSideHTML(repo) {
    const tags = repo.topics && repo.topics.length > 0 ? repo.topics.slice(0, 3) : ['GitHub', 'Project'];
    const description = repo.description || 'No description provided.';
    const topic = repo.topics && repo.topics[0] ? repo.topics[0].toUpperCase() : 'REPO';

    return `
        <a href="${repo.html_url}" target="_blank" class="project-side glass animate-fade-up" style="text-decoration: none; color: inherit; display: block;">
            <div class="project-details-sm">
                <span class="project-category">${topic}</span>
                <h3 class="project-title-text">${repo.name}</h3>
                <p>${description.length > 80 ? description.substring(0, 80) + '...' : description}</p>
                <div class="project-tags">
                    ${tags.map(tag => `<span>${tag}</span>`).join('')}
                </div>
            </div>
        </a>
    `;
}

function createArchiveCardHTML(repo) {
    const topic = repo.topics && repo.topics[0] ? repo.topics[0] : 'Software';
    return `
        <a href="${repo.html_url}" target="_blank" class="archive-item-link animate-fade-up" style="text-decoration: none; color: inherit; display: block;">
            <article class="archive-card">
                <div class="archive-img-box">
                    <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.03); font-weight: 800; color: var(--color-primary); font-family: var(--font-display); font-size: 1.2rem;"></div>
                    <div class="tech-badge-overlay">${repo.name}</div>
                </div>
                <div class="archive-content">
                    <span class="archive-tag">${topic}</span>
                    <h3 class="archive-item-title">${repo.name}</h3>
                    <p class="archive-item-desc">${repo.description || 'No description provided.'}</p>
                    <div class="archive-tags">
                        ${(repo.topics || []).slice(0, 3).map(t => `<span>${t}</span>`).join('')}
                    </div>
                </div>
            </article>
        </a>
    `;
}

async function renderProjects() {
    const homeContainer = document.getElementById('dynamic-projects-grid');
    const archiveContainer = document.getElementById('dynamic-archive-grid');

    if (!homeContainer && !archiveContainer) return;

    if (homeContainer) homeContainer.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px;">Loading projects...</div>';
    if (archiveContainer) archiveContainer.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px;">Fetching repositories...</div>';

    const repos = await fetchGithubRepos();
    if (!repos) return;

    // Home Page Logic
    if (homeContainer) {
        const featured = repos[0];
        const side = repos.slice(1); // display all remaining public repos in the sub-projects section
        let html = createProjectFeaturedHTML(featured);
        if (side.length > 0) {
            html += `<div class="projects-side-grid">${side.map(repo => createProjectSideHTML(repo)).join('')}</div>`;
        }
        homeContainer.innerHTML = html;
    }

    // Archive Page Logic - With Categorization
    if (archiveContainer) {
        const groups = {};
        repos.forEach(repo => {
            let category = 'Other Projects';
            if (repo.topics && repo.topics.length > 0) {
                for (const t of repo.topics) {
                    if (CATEGORY_MAP[t.toLowerCase()]) {
                        category = CATEGORY_MAP[t.toLowerCase()];
                        break;
                    }
                }
            }
            if (!groups[category]) groups[category] = [];
            groups[category].push(repo);
        });

        // Order categories (priority ones first)
        const order = ['Computer Vision', 'Data Analysis', 'Machine & Deep Learning', 'Generative AI', 'Software Development', 'Other Projects'];
        let archiveHtml = '';

        order.forEach(catName => {
            if (groups[catName] && groups[catName].length > 0) {
                archiveHtml += `
                    <h2 class="category-title" style="grid-column: 1 / -1; margin-top: 64px; margin-bottom: 32px; font-family: var(--font-display); font-size: 2rem; border-bottom: 1px solid var(--color-border); padding-bottom: 12px; display: flex; align-items: center; gap: 15px;">
                        <span style="width: 8px; height: 8px; background: var(--color-primary); border-radius: 50%; box-shadow: 0 0 10px var(--color-primary);"></span>
                        ${catName}
                    </h2>
                    <div class="archive-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; grid-column: 1 / -1;">
                        ${groups[catName].map(repo => createArchiveCardHTML(repo)).join('')}
                    </div>
                `;
            }
        });

        archiveContainer.innerHTML = archiveHtml;
        // Adjust container style to be a block (since children handle grid)
        archiveContainer.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', renderProjects);
