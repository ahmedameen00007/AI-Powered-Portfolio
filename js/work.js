/**
 * work.js — Work Showcase Page
 * Renders project video cards with descriptions from the Work/ folder.
 *
 * FIX: Cards are made visible immediately (no scroll-reveal dependency)
 *      so videos always appear regardless of IntersectionObserver timing.
 */

// ── Project Data ──────────────────────────────────────────────────────────────

const workProjects = [
  {
    id:       'closer',
    folder:   'Closer',
    file:     'Closer.mp4',
    titleKey: 'vid_closer_title',
    descKey:  'vid_closer_desc',
    tagsKey:  'vid_closer_tags',
  },
  {
    id:       'eagle_vision',
    folder:   'Eagle_Vision',
    file:     'Eagle_Vision.mp4',
    titleKey: 'vid_eagle_title',
    descKey:  'vid_eagle_desc',
    tagsKey:  'vid_eagle_tags',
  },
  {
    id:       'hr_validator',
    folder:   'HR_Validator',
    file:     'HR_Validator.mp4',
    titleKey: 'vid_hr_title',
    descKey:  'vid_hr_desc',
    tagsKey:  'vid_hr_tags',
  },
  {
    id:       'national_id',
    folder:   'NationalID_Reader',
    file:     'NationalID_Reader.mp4',
    titleKey: 'vid_national_title',
    descKey:  'vid_national_desc',
    tagsKey:  'vid_national_tags',
  },
  {
    id:       'sign_measure',
    folder:   'SignMeasure_AI',
    file:     'SignMeasure_AI.mp4',
    titleKey: 'vid_sign_title',
    descKey:  'vid_sign_desc',
    tagsKey:  'vid_sign_tags',
  },
];

// ── Hardcoded fallbacks (used if i18n.js fails to load) ──────────────────────

const fallbackEN = {
  vid_closer_title:   'Closer — AI-Powered Assistive Communication Devices',
  vid_closer_desc:    "Closer helps facilitate communication between deaf/hard-of-hearing and blind/visually impaired individuals through an integrated system of two smart devices: an AI-powered smart glasses and smartwatch. The system enables interaction between users by leveraging AI, Computer Vision, NLP, LLMs, and speech recognition to convert information across different communication modalities.",
  vid_closer_tags:    ['AI', 'Computer Vision', 'NLP', 'LLMs', 'Speech Recognition'],

  vid_eagle_title:    'Eagle Vision — Exam Cheating Detection',
  vid_eagle_desc:     "A Computer Vision system for monitoring students during exams in college computer labs, detecting potential cheating by analyzing eye movement and visual behavior. When suspicious behavior is detected, the system alerts the supervisor with options to warn the student or automatically lock their device.",
  vid_eagle_tags:     ['Computer Vision', 'AI Monitoring', 'Behavior Analysis', 'Eye Tracking', 'Object Detection', 'Real-time Surveillance'],

  vid_hr_title:       'HR Validator — Intelligent Document Validation',
  vid_hr_desc:        "An AI system for validating HR and official documents. The system identifies the document type, detects and extracts key data, then verifies multiple elements such as stamps, document data, and information consistency — using Computer Vision, OCR, and specialized validation models.",
  vid_hr_tags:        ['Document AI', 'OCR', 'Computer Vision', 'Document Classification', 'Document Validation', 'Stamp Detection', 'Data Extraction'],

  vid_national_title: 'National ID Reader — Document Intelligence',
  vid_national_desc:  'A system using Computer Vision and OCR to extract data from Egyptian national ID card images. The system recognizes the card, identifies key data regions, and converts information into structured data for digital systems.',
  vid_national_tags:  ['OCR', 'Computer Vision', 'Data Extraction', 'Document AI'],

  vid_sign_title:     'SignMeasure AI — Shop Signboard Measurement',
  vid_sign_desc:      "A Computer Vision system that helps identify and measure commercial shop signboards from a photo. The system analyzes the image, detects the sign, determines its dimensions, and calculates its area — enabling local authorities to apply fees or regulations based on the measured sign area.",
  vid_sign_tags:      ['Computer Vision', 'Object Detection', 'AI Measurement', 'Image Analysis', 'Data Extraction', 'Smart Government'],
};

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Safely get a translation, falling back to the built-in English copy. */
function getText(key) {
  if (window.i18n && typeof window.i18n.t === 'function') {
    const val = window.i18n.t(key);
    // i18n.t returns the key itself when not found — use fallback in that case
    if (val !== key) return val;
  }
  return fallbackEN[key] !== undefined ? fallbackEN[key] : key;
}

/** Zero-pad a number to 2 digits */
function pad2(n) {
  return String(n).padStart(2, '0');
}

// ── Render ─────────────────────────────────────────────────────────────────────

function renderVideoCards() {
  const grid = document.getElementById('videos-grid');
  if (!grid) return;

  // Clear existing content (handles re-renders on lang change)
  grid.innerHTML = '';

  if (!workProjects.length) {
    grid.innerHTML = `
      <div class="work-empty">
        <span class="work-empty-icon">🎬</span>
        <h2 class="work-empty-title">No Videos Yet</h2>
        <p class="work-empty-desc">Project showcases will appear here once uploaded to the Work folder.</p>
      </div>`;
    return;
  }

  workProjects.forEach((project, index) => {
    const videoSrc = 'Work/' + project.folder + '/' + project.file;
    const title    = getText(project.titleKey);
    const desc     = getText(project.descKey);
    const tags     = getText(project.tagsKey);

    const tagArray = Array.isArray(tags) ? tags : [tags];
    const tagsHTML = tagArray.map(function(tag) {
      return '<span class="video-tag">' + tag + '</span>';
    }).join('');

    const card = document.createElement('article');
    card.className = 'video-card';
    card.id = 'project-' + project.id;
    card.setAttribute('data-project-id', project.id);

    // Staggered fade-in via inline style animation
    card.style.cssText = [
      'opacity: 0',
      'transform: translateY(30px)',
      'animation: workCardReveal 0.6s cubic-bezier(0.22,1,0.36,1) forwards',
      'animation-delay: ' + (index * 0.12) + 's',
    ].join(';');

    card.innerHTML =
      '<div class="video-overlay-bar"></div>' +

      // ① Description ABOVE the video
      '<div class="video-description-area">' +
        '<div class="video-number">' + pad2(index + 1) + '</div>' +
        '<h2 class="video-card-title" data-i18n="' + project.titleKey + '">' + title + '</h2>' +
        '<p class="video-card-desc" data-i18n="' + project.descKey + '">' + desc + '</p>' +
        '<div class="video-tags">' + tagsHTML + '</div>' +
      '</div>' +

      // ② Video player BELOW the description
      '<div class="video-player-wrapper">' +
        '<video' +
        '  id="video-' + project.id + '"' +
        '  src="' + videoSrc + '"' +
        '  controls' +
        '  preload="metadata"' +
        '  aria-label="' + title + '"' +
        '  playsinline' +
        '>' +
        'Your browser does not support HTML5 video.' +
        '</video>' +
      '</div>';

  grid.appendChild(card);
  });

  initialRenderDone = true;
  // Smooth scroll to project card if referenced in hash
  scrollToHash();
}

let initialRenderDone = false;

/** Check URL hash and scroll/highlight the matching project card */
function scrollToHash() {
  const hash = window.location.hash;
  if (!hash) return;
  
  const targetId = 'project-' + hash.substring(1);
  const targetEl = document.getElementById(targetId);
  if (targetEl) {
    // Small delay to ensure rendering and DOM placement are complete
    setTimeout(() => {
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
      
      // Flash / highlight effect to draw focus
      targetEl.style.transition = 'box-shadow 0.5s ease, border-color 0.5s ease';
      targetEl.style.borderColor = 'var(--color-primary)';
      targetEl.style.boxShadow = '0 0 30px rgba(73, 31, 223, 0.4)';
      
      setTimeout(() => {
        targetEl.style.boxShadow = '';
        targetEl.style.borderColor = '';
      }, 2000);
    }, 200);
  }
}

// ── Inject the card reveal keyframe once ─────────────────────────────────────

(function injectKeyframe() {
  if (document.getElementById('work-card-keyframe')) return;
  const style = document.createElement('style');
  style.id = 'work-card-keyframe';
  style.textContent =
    '@keyframes workCardReveal {' +
    '  from { opacity: 0; transform: translateY(30px); }' +
    '  to   { opacity: 1; transform: translateY(0); }' +
    '}';
  document.head.appendChild(style);
}());

// ── Re-render on language change ───────────────────────────────────────────────

document.addEventListener('langchange', function() {
  renderVideoCards();
});

// ── Init ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function() {
  if (!initialRenderDone) {
    renderVideoCards();
  }
});
