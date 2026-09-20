\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{aick-thai-preprint}[2026/09/20 v1.0.1 Center for AI Civic Knowledge Thai Preprint]

% ================================================================
% CANONICAL HOUSE CLASS — CENTER FOR AI CIVIC KNOWLEDGE
% Thai-language preprint / theoretical / social-science papers
% Visual structure is intentionally locked. Authors should edit metadata
% and manuscript content in the .tex file, not this class.
% ================================================================

\LoadClass[11pt,a4paper]{article}

% --- Page / language ---
\RequirePackage[a4paper,top=23mm,bottom=23mm,left=25mm,right=25mm]{geometry}
\RequirePackage{fontspec}
\setmainfont{Laksaman}
\setsansfont{Garuda}
\setmonofont{DejaVu Sans Mono}
\XeTeXlinebreaklocale "th"
\XeTeXlinebreakskip=0pt plus 0.8pt
\RequirePackage{setspace}
\setstretch{1.15}
\RequirePackage{ragged2e}
\RequirePackage{enumitem}
\setlist{nosep,leftmargin=2em}

% --- Tables / figures / diagrams ---
\RequirePackage{booktabs,tabularx,longtable,array}
\RequirePackage{graphicx}
\RequirePackage{tikz}
\usetikzlibrary{arrows.meta,positioning,shapes.geometric,fit}

% --- Links / identity ---
\RequirePackage[hidelinks]{hyperref}
\RequirePackage{orcidlink}
\RequirePackage{xurl}
\RequirePackage{url}
\urlstyle{same}
\Urlmuskip=0mu plus 2mu
\emergencystretch=2.5em

% --- Headers / headings ---
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}
\RequirePackage{titlesec}
\RequirePackage{xcolor}
\RequirePackage{etoolbox}

\definecolor{AICKnavy}{HTML}{17385D}
\definecolor{AICKgold}{HTML}{B49250}
\definecolor{AICKgray}{HTML}{626B73}
\definecolor{AICKrulegray}{gray}{0.72}

\renewcommand{\figurename}{ภาพที่}
\renewcommand{\tablename}{ตารางที่}

\titleformat{\section}{\Large\bfseries\sffamily}{\thesection}{0.6em}{}
\titleformat{\subsection}{\large\bfseries\sffamily}{\thesubsection}{0.6em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\sffamily}{\thesubsubsection}{0.6em}{}
\setlength{\parindent}{1.5em}
\setlength{\parskip}{0.28em}

% --- Convenience ---
\newcommand{\eng}[1]{\textit{#1}}
\newcommand{\term}[1]{\textbf{#1}}
\newcommand{\doi}[1]{\href{https://doi.org/#1}{doi:#1}}

% ================================================================
% AUTHOR-EDITABLE METADATA API
% ================================================================
\def\AICK@title{[ชื่อบทความ]}
\def\AICK@subtitle{}
\def\AICK@author{[ชื่อผู้เขียน]}
\def\AICK@authorshort{[ผู้เขียน]}
\def\AICK@orcid{}
\def\AICK@affiliation{Center for AI Civic Knowledge}
\def\AICK@shorttitle{[ชื่อเรื่องย่อ]}
\def\AICK@version{v1.0}
\def\AICK@date{\today}
\def\AICK@abstract{}
\def\AICK@keywords{}
\def\AICK@logo{ai-civic-knowledge-full-logo.png}

\newcommand{\AICKTitle}[1]{\gdef\AICK@title{#1}}
\newcommand{\AICKSubtitle}[1]{\gdef\AICK@subtitle{#1}}
\newcommand{\AICKAuthor}[1]{\gdef\AICK@author{#1}}
\newcommand{\AICKAuthorShort}[1]{\gdef\AICK@authorshort{#1}}
\newcommand{\AICKORCID}[1]{\gdef\AICK@orcid{#1}}
\newcommand{\AICKAffiliation}[1]{\gdef\AICK@affiliation{#1}}
\newcommand{\AICKShortTitle}[1]{\gdef\AICK@shorttitle{#1}}
\newcommand{\AICKVersion}[1]{\gdef\AICK@version{#1}}
\newcommand{\AICKDate}[1]{\gdef\AICK@date{#1}}
\newcommand{\AICKAbstract}[1]{\gdef\AICK@abstract{#1}}
\newcommand{\AICKKeywords}[1]{\gdef\AICK@keywords{#1}}

% ================================================================
% LOCKED RUNNING IDENTITY
% ================================================================
\pagestyle{fancy}
\setlength{\headheight}{16.23pt}
\fancyhf{}
\fancyhead[L]{\small \AICK@authorshort}
\fancyhead[R]{\small \AICK@shorttitle}
\fancyfoot[L]{\small AI CIVIC KNOWLEDGE · PREPRINT · \AICK@version}
\fancyfoot[R]{\small หน้า \thepage\ / \pageref{LastPage}}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0pt}

\fancypagestyle{AICKfirstpage}{%
  \fancyhf{}%
  \fancyfoot[L]{\small AI CIVIC KNOWLEDGE · PREPRINT · \AICK@version}%
  \fancyfoot[R]{\small หน้า \thepage\ / \pageref{LastPage}}%
  \renewcommand{\headrulewidth}{0pt}%
  \renewcommand{\footrulewidth}{0pt}%
}

% ================================================================
% LOCKED FRONT MATTER
% - Logo is absolute overlay: it never pushes the title block.
% - Title system is left aligned.
% - Abstract + keywords are designed to remain on page 1.
% ================================================================
\newcommand{\AICKMakeFrontMatter}{%
  \thispagestyle{AICKfirstpage}%
  \begin{tikzpicture}[remember picture,overlay]
    \node[anchor=north east,inner sep=0pt]
      at ([xshift=-25mm,yshift=-9mm]current page.north east)
      {\includegraphics[width=31mm]{\AICK@logo}};
  \end{tikzpicture}%
  \noindent
  {\sffamily\bfseries\color{AICKnavy}\large PREPRINT}%
  {\sffamily\footnotesize\color{AICKgray}\hspace{0.7em}· \AICK@version · \AICK@date}%

  \vspace{3.2mm}
  \begin{flushleft}
  \begin{minipage}{0.78\textwidth}
  {\LARGE\bfseries\sffamily \AICK@title}\par
  \ifstrempty{\AICK@subtitle}{}{\vspace{1.2mm}{\large\bfseries\sffamily \AICK@subtitle}\par}%
  \vspace{3.2mm}
  {\normalsize \AICK@author%
    \ifstrempty{\AICK@orcid}{}{\,\orcidlink{\AICK@orcid}}%
    \;·\;\AICK@affiliation}%
  \end{minipage}
  \end{flushleft}

  \vspace{2.2mm}
  {\color{AICKgold}\hrule height 0.7pt}
  \vspace{2.4mm}

  \begin{spacing}{1.06}\small
  \noindent\textbf{บทคัดย่อ}\par
  \noindent\AICK@abstract

  % Canonical one-line breathing space between abstract and keywords.
  \par\vspace{\baselineskip}
  \noindent\textbf{คำสำคัญ:} \AICK@keywords
  \end{spacing}
  \clearpage
}

% ================================================================
% REQUIRED PAGE 2: METHODOLOGICAL / STATUS NOTE
% The note receives its own page. The next section therefore begins page 3.
% ================================================================
\newcommand{\AICKMethodologyPage}[1]{%
  \section*{สถานะบทความและวิถีวิทยาการสร้างความรู้}
  #1
  \clearpage
}

% --- End matter helpers ---
\newcommand{\AICKDeclarations}[1]{%
  \section*{คำประกาศของผู้เขียน}
  #1
}
\newcommand{\AICKAcknowledgements}[1]{%
  \section*{กิตติกรรมประกาศ}
  #1
}
\newenvironment{AICKReferences}{%
  \section*{เอกสารอ้างอิง}
  \begin{enumerate}[label={[\arabic*]},leftmargin=2.2em,itemsep=0.3em]
}{%
  \end{enumerate}
}

\endinput
