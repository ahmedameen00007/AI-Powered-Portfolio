/**
 * i18n.js — Bilingual Portfolio: English / Arabic
 * Professional translation by the portfolio owner.
 * Arabic font: Cairo (Google Fonts)
 */

// ─────────────────────────────────────────────────────────────────────────────
// TRANSLATION DICTIONARIES
// ─────────────────────────────────────────────────────────────────────────────

var translations = {

  // ══════════════════════════════════════════════════════════════════════
  // ENGLISH
  // ══════════════════════════════════════════════════════════════════════
  en: {

    // ── Navigation / Global ──────────────────────────────────────────
    back_btn:          'Back to Portfolio',
    nav_home:          'Home',

    // ── Hero ─────────────────────────────────────────────────────────
    hero_title:        'Ahmed Ameen',
    hero_tagline:      'Aspiring Generative AI Engineer aiming to solve real-world business problems through AI integration and intelligent solutions.',
    btn_view_work:     'View Work',
    btn_contact:       'Contact Me',

    // ── Floating Badges ───────────────────────────────────────────────
    badge_genai:       ' GenAI',
    badge_data:        ' Data Science',
    badge_llms:        ' LLMs',

    // ── About ────────────────────────────────────────────────────────
    about_label:       'Expertise',
    about_title:       'About Me',
    about_intro:       'Passionate AI specialist with a strong focus on Generative AI, Agentic Systems, Computer Vision, and Data Science. Dedicated to building intelligent, autonomous, and scalable AI solutions that address real-world problems.',

    card_genai:        'Generative AI',
    card_agentic:      'Agentic AI',
    card_datascience:  'Data Science',

    skill_llms:        'LLMs & Fine-Tuning',
    skill_rag:         'RAG Architectures',
    skill_prompt:      'Prompt Engineering',
    skill_agents:      'Autonomous Agents',
    skill_langchain:   'LangChain & LlamaIndex',
    skill_tools:       'Tool-Augmented LLMs',
    skill_ml:          'Machine Learning Models',
    skill_predictive:  'Predictive Analytics',
    skill_stats:       'Statistical Modeling',

    // ── Experience ───────────────────────────────────────────────────
    exp_label:         'Journey',
    exp_title:         'Experience',

    exp1_title:        'KFS Gov – Gen AI & Data Science Intern',
    exp1_date:         'Feb 2026 – Present',
    exp1_bullet1:      'Developed and contributed to AI solutions designed for real-world governmental applications across KFS Gov.',
    exp1_bullet2:      'Collaborated on scalable AI applications aimed at improving operational efficiency and decision-making.',

    exp2_title:        'Freelance – Gen AI Engineer & Data Scientist',
    exp2_date:         'Feb 2026 – Present',
    exp2_bullet1:      'Developed projects in Computer Vision, RAG systems, data analytics, and business intelligence dashboards.',
    exp2_bullet2:      'Built AI-powered solutions using Python, TensorFlow, Scikit-learn, and Generative AI technologies.',

    exp3_title:        'Hex Softwares Pvt. Ltd. – Data Science Intern',
    exp3_date:         'Jan 2026 – Feb 2026',
    exp3_bullet1:      'Applied data science and machine learning techniques to real-world datasets.',
    exp3_bullet2:      'Developed practical experience in end-to-end data science project execution.',

    exp4_title:        'NTI – Big Data Analysis Trainee',
    exp4_date:         'Jul 27 – Aug 21, 2025 | 120 Hours | 97.5% overall score',
    exp4_bullet1:      'Gained hands-on experience in data processing, analysis of large datasets, and analytics workflows.',
    exp4_bullet2:      'Learned freelancing fundamentals, including project delivery, client communication, and professional practices.',

    // ── Projects ─────────────────────────────────────────────────────
    projects_label:    'Portfolio',
    projects_title:    'Projects',
    btn_view_projects: 'View All Projects',

    // ── Certificates / Awards / Archive ─────────────────────────────
    cert_label:        'Achievements',
    cert_title:        'Certificates',
    awards_label:      'Recognition',
    awards_title:      'Honors & Awards',
    return_to_journey: 'RETURN TO JOURNEY',
    leaderboards:      'Certificates',
    elite_recognition: 'Elite Recognition',
    projects_archive:  'Projects Archive',
    projects_archive_desc: 'A comprehensive timeline of Engineering, Data Science, and AI Solutions.',
    personal_branding: 'Personal Branding',
    identity:          'Identity',

    // ── Contact ──────────────────────────────────────────────────────
    contact_label:     'Connection',
    contact_title:     "Let's Build the Future",
    contact_desc:      "I'm currently open to new opportunities and interesting collaborations to solve real-world business problems.",

    // ── work.html ─────────────────────────────────────────────────────
    page_title:        'Work Showcase | Ahmed Ameen',
    header_label:      'Showcase',
    page_heading:      'My Work',
    page_subheading:   "A curated collection of project demos, case studies, and AI solutions I've built.",
    loading_text:      'Loading videos…',
    footer_note:       'More projects coming soon — stay tuned!',

    // ── Project 01 — Closer ───────────────────────────────────────────
    vid_closer_title:   'Closer — AI-Powered Assistive Communication Devices',
    vid_closer_desc:    "Closer helps facilitate communication between deaf/hard-of-hearing and blind/visually impaired individuals through an integrated system of two smart devices: an AI-powered smart glasses and smartwatch. The system enables interaction between users by leveraging AI, Computer Vision, NLP, LLMs, and speech recognition to convert information across different communication modalities.",
    vid_closer_tags:    ['AI', 'Computer Vision', 'NLP', 'LLMs', 'Speech Recognition'],

    // ── Project 02 — Eagle Vision ────────────────────────────────────
    vid_eagle_title:    'Eagle Vision — Exam Cheating Detection',
    vid_eagle_desc:     "A Computer Vision system for monitoring students during exams in college computer labs, detecting potential cheating by analyzing eye movement and visual behavior. When suspicious behavior is detected, the system alerts the responsible supervisor with options to warn the student or automatically lock their device.",
    vid_eagle_tags:     ['Computer Vision', 'AI Monitoring', 'Behavior Analysis', 'Eye Tracking', 'Object Detection', 'Real-time Surveillance'],

    // ── Project 03 — HR Validator ─────────────────────────────────────
    vid_hr_title:       'HR Validator — Intelligent Document Validation',
    vid_hr_desc:        "An AI system for validating HR and official documents. The system identifies the document type, detects and extracts key data, then verifies multiple elements such as stamps, document data, and information consistency — using Computer Vision, OCR, and specialized validation models to produce a validation result with reasons for any issues found.",
    vid_hr_tags:        ['Document AI', 'OCR', 'Computer Vision', 'Document Classification', 'Document Validation', 'Stamp Detection', 'Data Extraction'],

    // ── Project 04 — NationalID Reader ───────────────────────────────
    vid_national_title: 'National ID Reader — Document Intelligence',
    vid_national_desc:  "A system using Computer Vision and OCR to extract data from Egyptian national ID card images. The system recognizes the card, identifies key data regions, extracts the information and converts it into structured data ready for use in digital systems and applications.",
    vid_national_tags:  ['OCR', 'Computer Vision', 'Data Extraction', 'Document AI'],

    // ── Project 05 — SignMeasure AI ───────────────────────────────────
    vid_sign_title:     'SignMeasure AI — Shop Signboard Measurement',
    vid_sign_desc:      "A Computer Vision system that helps identify and measure commercial shop signboards from a photo taken by the shop owner. The system analyzes the image, detects the sign, determines its dimensions, and calculates its area — enabling local authorities to accurately know the sign size and use the data for assessments, fee calculations, or regulation enforcement.",
    vid_sign_tags:      ['Computer Vision', 'Object Detection', 'AI Measurement', 'Image Analysis', 'Data Extraction', 'Smart Government'],

    // ── Project 06 — LeakLens ─────────────────────────────────────────
    vid_leaklens_title: 'LeakLens — AI-Powered Smart Water Management',
    vid_leaklens_desc:  'LeakLens is an AI-powered smart water management system designed to detect, analyze, and locate water leaks across water networks. By analyzing key network parameters such as flow rates and pressure levels, the system uses artificial intelligence to identify abnormal patterns, estimate the severity of leaks, and determine their potential locations. Once a leak is detected, LeakLens notifies the responsible engineers, enabling them to take the necessary action quickly and efficiently. The system also includes a mobile application for both engineers and citizens, facilitating communication, reporting water-related issues, monitoring leaks, and reviewing their status in real time.',
    vid_leaklens_tags:  ['AI', 'Water Management', 'Anomaly Detection', 'IoT', 'Mobile App', 'Smart Infrastructure'],
  },


  // ══════════════════════════════════════════════════════════════════════
  // ARABIC
  // ══════════════════════════════════════════════════════════════════════
  ar: {

    // ── Navigation / Global ──────────────────────────────────────────
    back_btn:          'العودة إلى معرض الأعمال',
    nav_home:          'الرئيسية',

    // ── Hero ─────────────────────────────────────────────────────────
    hero_title:        'أحمد أمين',
    hero_tagline:      'مهندس ذكاء اصطناعي توليدي طموح، أهدف إلى حل مشكلات الأعمال الواقعية من خلال دمج الذكاء الاصطناعي وتطوير حلول ذكية.',
    btn_view_work:     'معرض أعمالي',
    btn_contact:       'تواصل معي',

    // ── Floating Badges ───────────────────────────────────────────────
    badge_genai:       ' الذكاء الاصطناعي التوليدي',
    badge_data:        ' علم البيانات',
    badge_llms:        ' نماذج اللغة الكبيرة',

    // ── About ────────────────────────────────────────────────────────
    about_label:       'الخبرات',
    about_title:       'نبذة عني',
    about_intro:       'متخصص شغوف بالذكاء الاصطناعي، مع تركيز قوي على الذكاء الاصطناعي التوليدي، والأنظمة الوكيلة، والرؤية الحاسوبية، وعلوم البيانات. أعمل على بناء حلول ذكاء اصطناعي ذكية ومستقلة وقابلة للتوسع لمعالجة المشكلات الواقعية.',

    card_genai:        'الذكاء الاصطناعي التوليدي',
    card_agentic:      'الذكاء الاصطناعي الوكيلي',
    card_datascience:  'علم البيانات',

    skill_llms:        'نماذج اللغة الكبيرة والضبط الدقيق',
    skill_rag:         'معماريات التوليد المعزز بالاسترجاع',
    skill_prompt:      'هندسة الأوامر',
    skill_agents:      'الوكلاء المستقلون',
    skill_langchain:   'LangChain و LlamaIndex',
    skill_tools:       'نماذج اللغة الكبيرة المعززة بالأدوات',
    skill_ml:          'نماذج التعلم الآلي',
    skill_predictive:  'التحليلات التنبؤية',
    skill_stats:       'النمذجة الإحصائية',

    // ── Experience ───────────────────────────────────────────────────
    exp_label:         'المسيرة المهنية',
    exp_title:         'الخبرات',

    exp1_title:        'مبنى محافظة كفر الشيخ — متدرب ذكاء اصطناعي توليدي وعلوم بيانات',
    exp1_date:         'فبراير 2026 – حتى الآن',
    exp1_bullet1:      'ساهمت في تطوير حلول ذكاء اصطناعي مصممة لتطبيقات حكومية واقعية داخل محافظة كفر الشيخ.',
    exp1_bullet2:      'شاركت في تطوير تطبيقات ذكاء اصطناعي قابلة للتوسع بهدف تحسين الكفاءة التشغيلية ودعم عملية اتخاذ القرار.',

    exp2_title:        'مستقل – مهندس ذكاء اصطناعي توليدي وعالم بيانات',
    exp2_date:         'فبراير 2026 – حتى الآن',
    exp2_bullet1:      'طورت مشاريع في مجالات الرؤية الحاسوبية، وأنظمة التوليد المعزز بالاسترجاع، وتحليل البيانات، ولوحات معلومات ذكاء الأعمال.',
    exp2_bullet2:      'بنيت حلولاً مدعومة بالذكاء الاصطناعي باستخدام Python وTensorFlow وScikit-learn وتقنيات الذكاء الاصطناعي التوليدي.',

    exp3_title:        'Hex Softwares Pvt. Ltd. – متدرب علوم بيانات',
    exp3_date:         'يناير 2026 – فبراير 2026',
    exp3_bullet1:      'طبقت تقنيات علوم البيانات والتعلم الآلي على مجموعات بيانات واقعية.',
    exp3_bullet2:      'اكتسبت خبرة عملية في تنفيذ مشاريع علوم البيانات بشكل متكامل من البداية إلى النهاية.',

    exp4_title:        'المعهد القومي للاتصالات – متدرب تحليل البيانات الضخمة',
    exp4_date:         '27 يوليو – 21 أغسطس 2025 | 120 ساعة | التقدير الإجمالي 97.5%',
    exp4_bullet1:      'اكتسبت خبرة عملية في معالجة البيانات وتحليل مجموعات البيانات الكبيرة وسير عمل التحليلات.',
    exp4_bullet2:      'تعلمت أساسيات العمل الحر، بما في ذلك تسليم المشاريع، والتواصل مع العملاء، والممارسات المهنية.',

    // ── Projects ─────────────────────────────────────────────────────
    projects_label:    'معرض الأعمال',
    projects_title:    'المشاريع',
    btn_view_projects: 'عرض جميع المشاريع',

    // ── Certificates / Awards / Archive ─────────────────────────────
    cert_label:        'الإنجازات',
    cert_title:        'الشهادات',
    awards_label:      'التقدير',
    awards_title:      'التكريم والجوائز',
    return_to_journey: 'العودة إلى الرحلة',
    leaderboards:      'الشهادات',
    elite_recognition: 'التقدير المتميز',
    projects_archive:  'أرشيف المشاريع',
    projects_archive_desc: 'خط زمني شامل لمشاريع الهندسة وعلوم البيانات وحلول الذكاء الاصطناعي.',
    personal_branding: 'الهوية الشخصية',
    identity:          'الهوية',

    // ── Contact ──────────────────────────────────────────────────────
    contact_label:     'تواصل',
    contact_title:     'لنَبْنِ المستقبل معًا',
    contact_desc:      'أنا منفتح حاليًا على فرص جديدة وتعاونات مميزة للمساهمة في حل مشكلات الأعمال الواقعية.',

    // ── work.html ─────────────────────────────────────────────────────
    page_title:        'معرض المشاريع | أحمد أمين',
    header_label:      'معرض المشاريع',
    page_heading:      'معرض أعمالي',
    page_subheading:   'مجموعة مختارة من عروض المشاريع ودراسات الحالة وحلول الذكاء الاصطناعي التي قمت بتطويرها.',
    loading_text:      'جارٍ تحميل الفيديوهات…',
    footer_note:       'المزيد من المشاريع قريبًا — ترقبوا المزيد!',

    // ── Project 01 — Closer ───────────────────────────────────────────
    vid_closer_title:   'Closer — أجهزة ذكية لتمكين التواصل للصم والمكفوفين',
    vid_closer_desc:    'يساعد Closer على تسهيل التواصل بين الأشخاص الصم وضعاف السمع، والأشخاص المكفوفين وضعاف البصر، من خلال نظام متكامل يعتمد على جهازين ذكيين: نظارة ذكية وساعة ذكية مدعومتان بالذكاء الاصطناعي. يعمل النظام على تسهيل التفاعل والتواصل بين المستخدمين من خلال توظيف تقنيات الذكاء الاصطناعي والرؤية الحاسوبية لتحويل المعلومات بين الوسائط المختلفة بطريقة أكثر سهولة ومرونة.',
    vid_closer_tags:    ['الذكاء الاصطناعي', 'الرؤية الحاسوبية', 'معالجة اللغة الطبيعية', 'نماذج اللغة الكبيرة', 'التعرف على الكلام'],

    // ── Project 02 — Eagle Vision ────────────────────────────────────
    vid_eagle_title:    'Eagle Vision — اكتشاف الغش في الامتحانات',
    vid_eagle_desc:     'نظام Computer Vision لمراقبة الطلاب أثناء الامتحانات داخل معامل الكليات، واكتشاف حالات الغش المحتملة من خلال تحليل حركة العين والسلوك البصري للطالب. عند اكتشاف سلوك مشبوه، يرسل النظام تنبيهًا إلى المراقب المسؤول، مع توفير خيارات للتعامل مع الحالة، مثل إصدار إنذار للطالب أو إغلاق جهازه تلقائيًا.',
    vid_eagle_tags:     ['Computer Vision', 'المراقبة بالذكاء الاصطناعي', 'تحليل السلوك', 'تحليل حركة العين', 'اكتشاف الأجسام', 'المراقبة في الوقت الفعلي'],

    // ── Project 03 — HR Validator ─────────────────────────────────────
    vid_hr_title:       'HR Validator — التحقق الذكي من المستندات',
    vid_hr_desc:        'نظام ذكاء اصطناعي للتحقق من صحة مستندات الموارد البشرية والمستندات الرسمية. يبدأ النظام بالتعرف على نوع المستند، ثم يكتشف ويستخرج البيانات المهمة منه، ويتحقق من عناصر متعددة مثل الأختام وبيانات المستند وتوافق المعلومات الموجودة بداخله. يعتمد النظام على مجموعة من تقنيات Computer Vision و OCR ونماذج تحقق متخصصة لتحليل المستندات وإصدار نتيجة التحقق مع توضيح أسباب عدم الصلاحية عند وجود أي مشكلة.',
    vid_hr_tags:        ['Document AI', 'OCR', 'Computer Vision', 'تصنيف المستندات', 'التحقق من المستندات', 'نماذج التحقق', 'اكتشاف الأختام', 'استخراج البيانات'],

    // ── Project 04 — NationalID Reader ───────────────────────────────
    vid_national_title: 'National ID Reader — استخراج بيانات بطاقة الرقم القومي',
    vid_national_desc:  'نظام يعتمد على تقنيات Computer Vision و OCR لاستخراج البيانات من صور بطاقات الرقم القومي المصرية. يقوم النظام بالتعرف على البطاقة وتحديد مناطق البيانات المهمة، ثم استخراج المعلومات منها وتحويلها إلى بيانات منظمة يمكن استخدامها داخل الأنظمة والتطبيقات الرقمية.',
    vid_national_tags:  ['OCR', 'Computer Vision', 'استخراج البيانات', 'Document AI'],

    // ── Project 05 — SignMeasure AI ───────────────────────────────────
    vid_sign_title:     'SignMeasure AI — قياس لافتات المحلات',
    vid_sign_desc:      'نظام Computer Vision يساعد على تحديد وقياس لافتات المحلات التجارية من خلال صورة يلتقطها صاحب المحل للافتة. يقوم النظام بتحليل الصورة والتعرف على اللافتة، ثم تحديد أبعادها وحساب مساحتها. ويساعد ذلك الجهات المحلية على معرفة مساحة اللافتة بدقة، واستخدام البيانات الناتجة في إجراءات التقييم وتطبيق الرسوم أو اللوائح المرتبطة بها.',
    vid_sign_tags:      ['Computer Vision', 'اكتشاف الأجسام', 'القياس بالذكاء الاصطناعي', 'تحليل الصور', 'استخراج البيانات', 'الحكومة الذكية'],

    // ── Project 06 — LeakLens ─────────────────────────────────────────
    vid_leaklens_title: 'LeakLens — نظام ذكي لإدارة شبكات المياه',
    vid_leaklens_desc:  'LeakLens هو نظام ذكي لإدارة شبكات المياه باستخدام الذكاء الاصطناعي، يهدف إلى اكتشاف وتحليل وتحديد مواقع تسريبات المياه داخل الشبكة. يعتمد النظام على تحليل بيانات مهمة مثل معدلات تدفق المياه ومستويات الضغط لاكتشاف الأنماط غير الطبيعية، وتحديد وجود التسريبات، وتحليل شدتها، وتقدير موقعها المحتمل. وعند اكتشاف أي تسريب، يقوم النظام بإبلاغ المهندسين المسؤولين لاتخاذ الإجراءات اللازمة بسرعة وكفاءة. كما يدعم LeakLens تطبيقًا للهواتف المحمولة يخدم المهندسين والمواطنين، مما يسهّل الإبلاغ عن مشكلات المياه والتسريبات، وتحسين التواصل بين المواطنين والجهات المسؤولة، ومراجعة حالة البلاغات والتسريبات ومتابعتها.',
    vid_leaklens_tags:  ['الذكاء الاصطناعي', 'إدارة المياه', 'كشف الشذوذ', 'إنترنت الأشياء', 'تطبيق جوال', 'البنية التحتية الذكية'],
  }

}; // end translations


// ─────────────────────────────────────────────────────────────────────────────
// STATE
// ─────────────────────────────────────────────────────────────────────────────

var currentLang = localStorage.getItem('portfolio_lang') || 'en';


// ─────────────────────────────────────────────────────────────────────────────
// CORE HELPERS
// ─────────────────────────────────────────────────────────────────────────────

/** Return a translated string for the current language, falling back to EN. */
function t(key) {
  var dict = translations[currentLang];
  if (dict && dict[key] !== undefined) return dict[key];
  var en  = translations['en'];
  if (en  && en[key]  !== undefined) return en[key];
  return key;
}

/** Apply every [data-i18n] element on the page to the current language. */
function applyTranslations() {
  var isAr = (currentLang === 'ar');
  var dir  = isAr ? 'rtl' : 'ltr';

  // 1. Document lang + dir
  document.documentElement.setAttribute('lang', currentLang);
  document.documentElement.setAttribute('dir',  dir);

  // 2. <title data-i18n="…">
  var titleEl = document.querySelector('title[data-i18n]');
  if (titleEl) { document.title = t(titleEl.getAttribute('data-i18n')); }

  // 3. All [data-i18n] elements (strings only — arrays handled by work.js)
  var tagged = document.querySelectorAll('[data-i18n]');
  for (var i = 0; i < tagged.length; i++) {
    var el   = tagged[i];
    var key  = el.getAttribute('data-i18n');
    var text = t(key);
    if (typeof text === 'string') {
      el.textContent = text;
    }
  }

  // 4. Flip list indentation for RTL
  var lists = document.querySelectorAll('ul[style]');
  for (var j = 0; j < lists.length; j++) {
    if (isAr) {
      lists[j].style.paddingLeft  = '0';
      lists[j].style.paddingRight = '20px';
    } else {
      lists[j].style.paddingLeft  = '20px';
      lists[j].style.paddingRight = '0';
    }
  }

  // 5. Sync active state on language buttons
  var btns = document.querySelectorAll('.lang-btn');
  for (var k = 0; k < btns.length; k++) {
    var active = (btns[k].dataset.lang === currentLang);
    btns[k].classList.toggle('lang-btn--active', active);
    btns[k].setAttribute('aria-pressed', String(active));
  }

  // 6. Fire event so work.js can re-render video cards
  document.dispatchEvent(new CustomEvent('langchange', { detail: { lang: currentLang } }));
}

/** Switch language, persist to localStorage. */
function setLanguage(lang) {
  if (!translations[lang]) return;
  currentLang = lang;
  localStorage.setItem('portfolio_lang', lang);
  applyTranslations();
}


// ─────────────────────────────────────────────────────────────────────────────
// LANGUAGE SWITCHER BUTTONS
// ─────────────────────────────────────────────────────────────────────────────

function initLangSwitcher() {
  var btns = document.querySelectorAll('.lang-btn');
  for (var i = 0; i < btns.length; i++) {
    (function(btn) {
      btn.addEventListener('click', function() {
        setLanguage(btn.dataset.lang);
      });
    }(btns[i]));
  }
}


// ─────────────────────────────────────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function() {
  initLangSwitcher();
  applyTranslations();
});

// Expose helpers for work.js
window.i18n = {
  t:           t,
  setLanguage: setLanguage,
  currentLang: function() { return currentLang; }
};
