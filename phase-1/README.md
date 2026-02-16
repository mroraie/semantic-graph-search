# فاز اول — تحلیل مسئله، طراحی الگوریتم و ساختاردهی اولیه

<div class="md-flex">
  <div class="md-text">
    پروژه درس <strong>طراحی الگوریتم‌ها</strong> فاز اول - ترم 4041<br>
    نام دانشجو: <strong>محمدرضا اورعی</strong> <br>
    شماره دانشجویی: <strong>40318253</strong>
  </div>
  <div class="md-image">
    <img src="logo1.png" alt="logo">
  </div>
</div>

## توضیح کلی مسئله
فاز اول این پروژه به تحلیل دقیق مسئله‌ی **جستجو در گراف معنایی** و طراحی چارچوب الگوریتمی آن اختصاص دارد. در این فاز، مفاهیم به‌صورت گره‌های یک گراف وزن‌دار مدل شده‌اند که وزن یال‌ها بیانگر میزان شباهت معنایی بین مفاهیم است و مسئله به یافتن مسیر معنایی بهینه بین دو گره تقلیل داده می‌شود. ابتدا مسئله به‌طور رسمی تعریف شده و ورودی‌ها، خروجی‌ها و معیارهای ارزیابی به‌صورت قابل اندازه‌گیری مشخص شده‌اند، سپس الگوریتم‌های کلاسیک جستجو و کوتاه‌ترین مسیر شامل BFS، DFS، Dijkstra، A*، Floyd–Warshall و یک روش Hybrid انتخاب و طراحی شده‌اند. در ادامه، تحلیل زمانی و فضایی هر الگوریتم با استفاده از Big-O ارائه شده و شرایط مناسب استفاده از هر کدام بررسی گردیده است. همچنین نقش احتمالی LLM صرفاً به‌عنوان ماژول محاسبه شباهت یا ارزیاب کیفیت مسیرها تعریف شده و هسته‌ی الگوریتمی پروژه کاملاً مستقل از آن باقی مانده است. این فاز پایه‌ی نظری و ساختاری لازم برای پیاده‌سازی و مقایسه‌ی تجربی الگوریتم‌ها در فازهای بعدی را فراهم می‌کند.

## فهرست مطالب

1. [اهداف فاز ۱](#۱-اهداف-فاز-۱)  
2. [تعریف دقیق مسئله](#۲-تعریف-دقیق-مسئله)  
3. [تحلیل مسئله (Problem Analysis)](#۳-تحلیل-مسئله-problem-analysis)  
4. [طراحی الگوریتم](#۴-طراحی-الگوریتم)  
5. [تحلیل زمان و فضا (Time & Space Complexity)](#۵-تحلیل-زمان-و-فضا-time--space-complexity)  
6. [تعیین نقش LLM (در صورت وجود)](#۶-تعیین-نقش-llm-در-صورت-وجود)  
7. [شبه‌کد الگوریتم‌ها و خلاصه پیچیدگی](#۷-شبه‌کد-الگوریتم‌ها-و-خلاصه-پیچیدگی)  

<div style="page-break-after: always;"></div>

## ۱. اهداف فاز ۱
1.  **تحلیل مسئله:** بررسی ساختار گراف معنایی و روابط بین مفاهیم.
2.  **طراحی الگوریتم:** پیاده‌سازی هسته الگوریتم‌های BFS, DFS, Dijkstra, A*, Floyd-Warshall.
3.  **تحلیل پیچیدگی:** محاسبه زمان و فضای مورد نیاز هر الگوریتم.
4.  **ساختاردهی:** ایجاد کلاس‌ها و توابع پایه برای مدیریت گراف.


## ۲. تعریف دقیق مسئله
  در این پروژه هدف، طراحی و پیاده‌سازی یک «سامانه جستجو روی گراف معنایی» است. در این سامانه، مجموعه‌ای از مفاهیم (کلمات یا عبارات) به صورت گره‌های یک گراف جهت‌دار مدل می‌شوند و بین هر دو گره که از نظر معنایی مرتبط هستند، یالی با وزن شباهت در بازه \([0, 1]\) قرار داده می‌شود. مسئله اصلی این است که برای یک جفت مفهوم مبدأ و مقصد، **مسیر (یا مسیرهای) معنایی بهینه** بین آن‌ها را با استفاده از الگوریتم‌های مختلف جستجو، پیدا کنیم و عملکرد این الگوریتم‌ها را از نظر کیفیت مسیر، تعداد گره‌های پیمایش‌شده، زمان اجرا و مصرف حافظه **به‌صورت کمی و قابل اندازه‌گیری** مقایسه کنیم.

### **ساختار ورودی ها و خروجی ها**
![[111111111111/algo/phase_1/imgs/inout.png]]
- **ورودی (Input) مسئله**  
  ورودی‌های سامانه به صورت شفاف و دقیق به شکل زیر تعریف می‌شوند:
  - **مجموعه مفاهیم**: لیستی از کلمات/عبارات که قرار است در گراف معنایی به عنوان گره استفاده شوند.  
  - **ماتریس شباهت یا تابع شباهت**:  
    - یا یک ماتریس \(N \times N\) از مقادیر شباهت معنایی بین هر جفت مفهوم (`similarity_matrix`)،  
    - یا یک ماژول محاسبه شباهت که برای هر جفت مفهوم یک مقدار در بازه \([0, 1]\) برمی‌گرداند.  
  - **آستانه شباهت (`similarity_threshold`)**: حداقلی که اگر شباهت دو مفهوم کمتر از آن باشد، بین آن‌ها یال ساخته نمی‌شود.  
  - **جفت سؤال جستجو**:  
    - گره مبدأ (`start`)  
    - گره مقصد (`goal`)  
  - **الگوریتم انتخاب‌شده و پارامترهای آن**:  
    - نوع الگوریتم: `BFS`, `DFS`, `Dijkstra`, `A*`, `Hybrid`, `Floyd–Warshall`  
    - پارامترها مانند `max_depth`، `min_similarity`، تابع heuristic در A* و … .

- **خروجی (Output) مسئله**  
  خروجی سامانه برای هر پرسش جستجو شامل موارد زیر است:
  - **مسیر معنایی پیدا شده**: دنباله‌ای از گره‌ها از مبدأ تا مقصد.  
  - **کیفیت مسیر**:  
    - شباهت کلی مسیر (مثلاً حاصل‌ضرب شباهت یال‌ها یا هزینه \(-\log(sim)\)).  
    - طول مسیر (تعداد یال‌ها).  
  - **آمار اجرایی الگوریتم**:  
    - تعداد گره‌های بازدید شده و گره‌های واقعاً اکسپلور شده.  
    - زمان اجرا (بر اساس اندازه گراف و آمار تجربی).  
    - تخمین یا گزارش مصرف حافظه.  
  - **گزارش مقایسه‌ای** (در حالت تحلیل): جدولی که الگوریتم‌های مختلف را از نظر پیچیدگی زمانی/فضایی تئوری (`AlgorithmComplexityAnalyzer`) و نتایج تجربی روی گراف‌های مختلف (`GraphMetrics`) مقایسه می‌کند.

### **مقایسه نسخه ساده و نسخه پیچیده مسئله**  
![[compersions.png]]
  - **نسخه ساده مسئله**:  
    - گراف معنایی روی یک مجموعه کوچک و محدود از مفاهیم (مثلاً ۲۰–۵۰ کلمه) به صورت دستی یا با یک ماتریس شباهت ثابت ساخته می‌شود.  
    - فقط برخی الگوریتم‌ها (مثلاً `SemanticBFS` و `SemanticDijkstra`) روی این گراف اجرا می‌شوند.  
    - معیارهای اندازه‌گیری محدود به طول مسیر و تعداد گره‌های بازدید شده است.  
    - هدف در این نسخه، **درک رفتار الگوریتم‌ها و صحت پیاده‌سازی** است، نه بهینه‌سازی شدید عملکرد.  

  - **نسخه پیچیده مسئله**:  
    - گراف معنایی روی یک مجموعه بزرگ‌تر و نزدیک‌تر به دنیای واقعی از مفاهیم ساخته می‌شود (مثلاً صدها یا هزاران گره) و یال‌ها با استفاده از روش‌های محاسبه شباهت خودکار تولید می‌شوند.  
    - تمام الگوریتم‌های جستجو (`BFS`, `DFS`, `Dijkstra`, `A*`, `Hybrid`, `Floyd–Warshall`) اجرا و با هم مقایسه می‌شوند.  
    - علاوه بر صحت مسیر، **معیارهای عملکردی** شامل زمان اجرا، مصرف حافظه، تعداد گره‌های بررسی‌شده و تحلیل چگالی گراف (`GraphMetrics`) اندازه‌گیری می‌شوند.  
    - خروجی شامل **گزارش تحلیلی کامل** و توصیه‌ی انتخاب الگوریتم مناسب برای انواع گراف‌ها (کوچک/بزرگ، متراکم/پراکنده) است.




<div style="page-break-after: always;"></div>

## فایل‌های موجود:
- `semantic_graph.py`: ساختار داده گراف معنایی.
- `algorithms.py`: پیاده‌سازی الگوریتم‌های جستجو.
- `analysis.py`: تحلیل پیچیدگی‌های زمانی و فضایی.

## ۳. تحلیل مسئله (Problem Analysis)

- **موضوع در کدام دسته از الگوریتم‌هاست؟**  
  مسئله این پروژه در دسته‌ی **الگوریتم‌های گراف و جستجو روی گراف** قرار می‌گیرد. به طور دقیق‌تر، با یک گراف وزن‌دار (وزن‌ها معکوس شباهت معنایی هستند) سروکار داریم و الگوریتم‌های کلاسیک **پیمایش گراف (BFS/DFS)**، **کوتاه‌ترین مسیر (Dijkstra, A\*, Floyd–Warshall)** و یک الگوریتم **ترکیبی (Hybrid)** را روی این گراف پیاده‌سازی و مقایسه می‌کنیم. بخش بهینه‌سازی در اینجا به معنای **یافتن مسیری با بیشترین شباهت / کمترین هزینه** بین دو مفهوم است.

- **آیا مسئله NP-hard است؟ آیا نیاز به تقریب دارد؟**  
  در این پروژه، ساختار گراف و تابع هزینه به‌گونه‌ای انتخاب شده که مسئله به **مسئله‌ی استاندارد کوتاه‌ترین مسیر در گراف وزن‌دار** تقلیل پیدا می‌کند. این مسئله با الگوریتم‌هایی مثل Dijkstra و Floyd–Warshall در زمان چندجمله‌ای حل می‌شود و **NP-hard نیست**. بنابراین برای نسخه‌ای که در این پروژه پیاده‌سازی شده، **نیازی به الگوریتم‌های تقریبی یا روش‌های فراابتکاری** وجود ندارد؛ الگوریتم‌های دقیق (Exact) پاسخ بهینه را در زمان قابل قبول برای اندازه‌های هدف ما برمی‌گردانند. تنها در گراف‌های بسیار بزرگ یا سناریوهای بلادرنگ، ممکن است در آینده از نسخه‌های تقریبی یا هیوریستیکی (مثلاً A\* با heuristic تهاجمی‌تر) استفاده شود.

- **آیا LLM نقشی در مسئله دارد؟ اگر دارد چه نقشی و در کدام مرحله؟**  
  هسته‌ی مسئله و الگوریتم‌ها **کاملاً کلاسیک و مستقل از LLM تولید متن** طراحی شده‌اند؛ یعنی جستجو و محاسبات گرافی صرفاً روی ساختار `SemanticGraph` و وزن‌های شباهت انجام می‌شود و بدون نیاز به مدل زبانی هم قابل اجرا و تحلیل است. با این حال، برای بخش شباهت معنایی می‌توان از یک مدل امبدینگ فارسی مانند **`persian-embeddings.gguf`** استفاده کرد که نقش «اوراکل شباهت» را بر عهده می‌گیرد:
  - **محاسبه‌ی شباهت‌های معنایی بین مفاهیم**: برای هر کلمه/عبارت، بردار امبدینگ تولید می‌شود و شباهت بین دو مفهوم با شباهت کسینوسی بین این بردارها به‌دست می‌آید؛ این مقدار در بازه \([0, 1]\) به‌عنوان وزن یال در گراف استفاده می‌شود.  
  - در صورت نیاز، همچنان می‌توان از یک LLM تولید متن (یا همین مدل در نقش محدودتر) برای **توضیح متنی مسیر معنایی پیدا شده** یا **پیشنهاد تنظیمات الگوریتم** در گزارش نهایی استفاده کرد.  
  در فاز ۱، تأکید روی این است که **الگوریتم‌های گرافی مستقل باشند** و مدل‌هایی مثل `persian-embeddings.gguf` فقط در نقش ماژول محاسبه شباهت (Similarity Oracle) به کار گرفته شوند، نه به‌عنوان بخشی از خود الگوریتم‌های جستجو.

<div style="page-break-after: always;"></div>

## ۴. طراحی الگوریتم

- **الگوریتم‌های پایه**  
  برای حل مسئله ابتدا چند الگوریتم پایه انتخاب شده‌اند که هسته‌ی کار را انجام می‌دهند:
  - الگوریتم **Semantic BFS**: نسخه‌ی معنایی الگوریتم BFS که گره‌ها را بر حسب شباهت مرتب می‌کند و مسیرهای کوتاه و پرشباهت را سریع پیدا می‌کند.  
  - الگوریتم **Semantic Dijkstra**: الگوریتم کلاسیک کوتاه‌ترین مسیر با تبدیل شباهت به هزینه (مثلاً \(-\log(sim)\)) که مسیر بهینه جهانی را تضمین می‌کند.  
  - الگوریتم **Semantic A\***: بهبود Dijkstra با استفاده از تابع heuristic برای کاهش تعداد گره‌های بررسی‌شده.  
  شبه‌کد این الگوریتم‌ها به ترتیب در بخش‌های «۱. Semantic BFS»، «۲. Semantic Dijkstra» و «۳. Semantic A*» همین فایل آمده است.

- **الگوریتم‌های جایگزین و مقایسه‌ای**  
  برای تحلیل بهتر رفتار الگوریتم‌ها و مقایسه، موارد زیر به‌عنوان نسخه‌های جایگزین و مکمل در نظر گرفته شده‌اند:
  - در **DFS معنایی** (در کد `algorithms.py`) برای مقایسه‌ی پیمایش عمقی با BFS در گراف معنایی.  
  - در **Floyd–Warshall معنایی** برای محاسبه‌ی همه‌ی کوتاه‌ترین مسیرها به‌صورت یک‌جا، مناسب برای تحلیل کلی ساختار گراف و مقایسه با الگوریتم‌های تک‌مبدأ.  
  - استفاده از تنظیمات مختلف برای آستانه شباهت (`similarity_threshold`) و پارامترهای heuristic در A\* جهت مشاهده‌ی تأثیر آن‌ها بر کیفیت مسیر و زمان اجرا.

- **نسخه‌ی بهینه‌شده‌ی Hybrid**  
  با توجه به این‌که BFS در مسیرهای کوتاه بسیار سریع است و Dijkstra در تضمین بهینگی قوی عمل می‌کند، یک نسخه‌ی **Hybrid** طراحی شده که ابتدا با BFS تا عمق مشخص (`bfs_depth_limit`) به دنبال مسیر می‌گردد و فقط در صورت نیاز Dijkstra را اجرا می‌کند:
  - اگر مسیر کوتاه و قابل قبول باشد، هزینه کل فقط \(O(V + E)\) باقی می‌ماند.  
  - اگر مسیر پیچیده باشد، Dijkstra اجرا شده و مسیر واقعاً بهینه پیدا می‌شود.  
  شبه‌کد این طراحی در بخش «۴. Hybrid Search» آمده است.

- **استاندارد بودن Pseudocode و توضیح مراحل**  
  تمام شبه‌کدها در این README با سبک یکسان و نزدیک به استاندارد کتاب‌های طراحی الگوریتم (تعریف دقیق `INPUT/OUTPUT`، استفاده از ساختارهای `Queue`, `MinHeap`, `Map`, `Set` و ...) نوشته شده‌اند. برای هر الگوریتم:
  - **ورودی‌ها و خروجی‌ها** در ابتدا به‌صورت صریح مشخص شده‌اند.  
  - **حلقه‌ی اصلی و شرط پایان** دقیق بیان شده تا بتوان راحت آن را به کد پایتون (`algorithms.py`) نگاشت.  
  - در انتهای هر شبه‌کد، **پیچیدگی زمانی و فضایی** نوشته شده تا بخش تحلیل پیچیدگی مستقیماً به آن ارجاع دهد.

- **مثال‌های دستی (Hand-crafted Examples)**  
  برای درک بهتر رفتار الگوریتم‌ها و صحت‌سنجی پیاده‌سازی، چند مثال ساده‌ی دستی طراحی شده است؛ در این مثال‌ها:
  - مجموعه‌ای کوچک از مفاهیم (مثلاً `["AI", "ML", "Deep Learning", "Graph", "Search"]`) انتخاب و بین آن‌ها شباهت‌های مشخص (مانند ۰٫۹، ۰٫۷، ۰٫۳ و ...) تعریف می‌شود.  
  - بر روی این گراف کوچک، الگوریتم‌های `SemanticBFS`, `SemanticDijkstra`, `SemanticAStar` و `Hybrid` اجرا می‌شوند و مسیر خروجی آن‌ها به‌صورت مرحله‌به‌مرحله تحلیل می‌شود.  
  این مثال‌ها در فایل‌های کد مانند `examples.py` و در گزارش نهایی استفاده می‌شوند تا نشان دهند هر الگوریتم در چه شرایطی چه رفتاری دارد.

<div style="page-break-after: always;"></div>

## ۵. تحلیل زمان و فضا (Time & Space Complexity)
- **تحلیل Big-O کلی**  
  در این پروژه پیچیدگی تمام الگوریتم‌ها برحسب تعداد گره‌ها \(V\) و تعداد یال‌ها \(E\) و به‌صورت Big-O تحلیل شده است:
  - در **BFS / DFS:** زمان \(O(V + E)\)، فضا \(O(V)\).  
  - در **Dijkstra / A\*:** زمان \(O((V + E)\log V)\)، فضا \(O(V)\).  
  - در **Floyd–Warshall:** زمان \(O(V^3)\)، فضا \(O(V^2)\).  
  این مقادیر با پیاده‌سازی واقعی در `algorithms.py` و تحلیل تئوری در `analysis.py` هم‌خوان هستند.

- **بهترین حالت / میانگین / بدترین حالت**  
  بر اساس کلاس `AlgorithmComplexityAnalyzer`، برای هر الگوریتم سه حالت اصلی به‌صورت زیر خلاصه می‌شود:
  - در **Semantic BFS:**  
    - بهترین حالت: \(O(1)\) (وقتی مقصد همسایه‌ی مستقیم مبدأ است).  
    - میانگین و بدترین حالت: \(O(V + E)\) از نظر زمان، و \(O(V)\) از نظر فضا.  
  - در **Dijkstra:**  
    - بهترین حالت با heap: حدود \(O(V \log V)\).  
    - میانگین و بدترین حالت: \(O((V + E)\log V)\) با استفاده از صف اولویت‌دار.  
    - فضا در همه حالات: \(O(V)\).  
  - در **A\*:**  
    - از نظر Big-O در بدترین حالت مشابه Dijkstra است \(O((V + E)\log V)\)، اما در عمل با heuristic مناسب تعداد گره‌های بررسی‌شده کمتر می‌شود.  
  - در **Hybrid (BFS + Dijkstra):**  
    - بهترین حالت: وقتی BFS مسیر کوتاه را پیدا کند، زمان تقریباً \(O(V + E)\).  
    - میانگین و بدترین حالت: اجرای BFS به‌علاوه Dijkstra → \(O((V + E)\log V)\) و فضا \(O(V)\).
![[imhs.png]]
**نکات:**
- V = تعداد گره‌ها
- E = تعداد یال‌ها
- در گراف متراکم: E ≈ V²
- در گراف پراکنده: E ≈ V



### **مقایسه نسخه‌های مختلف الگوریتم**  
  با توجه به ساختار گراف (پراکنده یا متراکم بودن) و نیاز به بهینگی، می‌توان انتخاب زیر را توصیه کرد:
  - برای **گراف‌های کوچک یا پرسش‌های سریع**: استفاده از Semantic BFS کافی و ساده است.  
  - برای **مسیرهای کاملاً بهینه در گراف‌های بزرگ‌تر**: Dijkstra یا A\* مناسب است (A\* با heuristic خوب سریع‌تر است).  
  - برای **کاربردهای عمومی** که تعادل بین سرعت و کیفیت مهم است: نسخه‌ی Hybrid بهترین گزینه است، چون در مسیرهای کوتاه مانند BFS عمل می‌کند و در موارد پیچیده به Dijkstra سوئیچ می‌کند.  
  - در **تحلیل آفلاین ساختار گراف** یا نیاز به همه‌مسیرها، Floyd–Warshall با وجود هزینه‌ی بالاتر، دید کامل‌تری از گراف می‌دهد.

<div style="page-break-after: always;"></div>

## ۶. تعیین نقش LLM

در فاز اول، هسته‌ی الگوریتمی پروژه مستقل از LLM طراحی شده است، اما اگر از مدل زبانی بزرگ استفاده شود، بهترین جایگاه‌های آن در این سیستم به صورت زیر است:

- **محاسبه‌ی شباهت (Similarity Computation)**  
  LLM می‌تواند به‌عنوان یک **اوراکل معنایی** برای تخصیص وزن یال‌ها استفاده شود؛ یعنی به‌جای یا در کنار روش‌های بردار嵌ه (Embedding)، از مدل خواسته می‌شود میزان نزدیکی معنایی دو مفهوم را در بازه \([0, 1]\) برگرداند و این مقدار به‌صورت مستقیم به‌عنوان وزن شباهت در `SemanticGraph` ذخیره شود.

- **تولید کاندید (Candidate Generation)**  
  قبل از اجرای الگوریتم‌های گراف، LLM می‌تواند بر اساس توضیح متنی مسئله، **مجموعه‌ی اولیه‌ی مفاهیم و روابط پیشنهادی** را تولید کند (مثلاً استخراج کلمات کلیدی، پیشنهاد گره‌های واسط بین دو مفهوم، یا گسترش یک گره به مفاهیم مرتبط). این خروجی سپس به عنوان ورودی به ماژول ساخت گراف و الگوریتم‌های `BFS`, `Dijkstra`, `A*`, `Hybrid` داده می‌شود.

- **بررسی کیفیت پاسخ / Oracle-based Model**  
  پس از آن‌که الگوریتم مسیر یا مجموعه‌ای از مسیرها را پیدا کرد، می‌توان از LLM به عنوان یک **مدل اوراکل** استفاده کرد تا:
  - کیفیت معنایی مسیرهای پیدا شده را ارزیابی و رتبه‌بندی کند؛  
  - توضیح متنی برای هر مسیر ارائه دهد و در صورت نیاز مسیرهای ضعیف را فیلتر کند.  
  در این حالت، هسته‌ی تصمیم‌گیری گرافی همچنان توسط الگوریتم‌های کلاسیک انجام می‌شود و LLM صرفاً نقش **ارزیاب و ناظر کیفیت (Oracle)** را بر عهده دارد.

<div style="page-break-after: always;"></div>


## ۷. شبه‌کد الگوریتم‌ها و خلاصه پیچیدگی

### ۷.۱ الگوریتم Semantic BFS
![[khjs.png]]

```
ALGORITHM SemanticBFS(graph, start, goal, min_similarity)
INPUT: 
    graph: گراف معنایی
    start: گره مبدأ
    goal: گره مقصد
    min_similarity: حداقل شباهت برای عبور از یال

OUTPUT: مسیر از start به goal یا NULL

BEGIN
    IF start == goal THEN
        RETURN [start]
    END IF
    
    queue ← Queue()
    queue.enqueue((start, [start], 1.0))
    visited ← Set()
    visited.add(start)
    
    WHILE queue is not empty DO
        (current, path, current_sim) ← queue.dequeue()
        
        neighbors ← graph.getNeighbors(current)
        SORT neighbors BY similarity DESCENDING
        
        FOR EACH edge IN neighbors DO
            IF edge.similarity < min_similarity THEN
                CONTINUE
            END IF
            
            neighbor ← edge.target
            
            IF neighbor == goal THEN
                RETURN path + [neighbor]
            END IF
            
            IF neighbor NOT IN visited THEN
                visited.add(neighbor)
                new_path ← path + [neighbor]
                new_sim ← current_sim * edge.similarity
                queue.enqueue((neighbor, new_path, new_sim))
            END IF
        END FOR
    END WHILE
    
    RETURN NULL  // مسیر پیدا نشد
END
```

<div style="page-break-after: always;"></div>

**پیچیدگی:**
- زمان: O(V + E) در حالت عادی
- فضا: O(V)


### ۷.۲ الگوریتم Semantic Dijkstra
![[cjhgfvyjt.png]]

```
ALGORITHM SemanticDijkstra(graph, start, goal, similarity_to_distance)
INPUT:
    graph: گراف معنایی
    start: گره مبدأ
    goal: گره مقصد
    similarity_to_distance: تابع تبدیل شباهت به فاصله

OUTPUT: مسیر بهینه از start به goal یا NULL

BEGIN
    IF start == goal THEN
        RETURN [start]
    END IF
    
    distances ← Map()  // distance from start
    distances[start] ← 0.0
    previous ← Map()   // previous node in path
    previous[start] ← NULL
    
    heap ← MinHeap()
    heap.insert((0.0, start))
    visited ← Set()
    
    WHILE heap is not empty DO
        (current_dist, current) ← heap.extractMin()
        
        IF current IN visited THEN
            CONTINUE
        END IF
        
        visited.add(current)
        
        IF current == goal THEN
            path ← []
            node ← goal
            WHILE node ≠ NULL DO
                path.prepend(node)
                node ← previous[node]
            END WHILE
            RETURN path
        END IF
        
        FOR EACH edge IN graph.getNeighbors(current) DO
            neighbor ← edge.target
            
            IF neighbor IN visited THEN
                CONTINUE
            END IF
            
            edge_distance ← similarity_to_distance(edge.similarity)
            new_distance ← current_dist + edge_distance
            
            IF neighbor NOT IN distances OR new_distance < distances[neighbor] THEN
                distances[neighbor] ← new_distance
                previous[neighbor] ← current
                heap.insert((new_distance, neighbor))
            END IF
        END FOR
    END WHILE
    
    RETURN NULL  // path not found
END
```

**پیچیدگی:**
- زمان: O((V + E) log V)
- فضا: O(V)

### ۷.۳ الگوریتم Semantic A*
![[fovuhs.png]]

```
ALGORITHM SemanticAStar(graph, start, goal, heuristic, similarity_to_distance)
INPUT:
    graph: گراف معنایی
    start: گره مبدأ
    goal: گره مقصد
    heuristic: تابع heuristic (فاصله تخمینی)
    similarity_to_distance: تابع تبدیل شباهت به فاصله

OUTPUT: مسیر بهینه از start به goal یا NULL

BEGIN
    IF start == goal THEN
        RETURN [start]
    END IF
    
    g_score ← Map()  // real cost from start
    g_score[start] ← 0.0
    
    f_score ← Map()  // f(n) = g(n) + h(n)
    f_score[start] ← heuristic(start, goal)
    
    previous ← Map()
    previous[start] ← NULL
    
    heap ← MinHeap()
    heap.insert((f_score[start], 0.0, start))
    visited ← Set()
    
    WHILE heap is not empty DO
        (current_f, current_g, current) ← heap.extractMin()
        
        IF current IN visited THEN
            CONTINUE
        END IF
        
        visited.add(current)
        
        IF current == goal THEN
            path ← []
            node ← goal
            WHILE node ≠ NULL DO
                path.prepend(node)
                node ← previous[node]
            END WHILE
            RETURN path
        END IF
        
        FOR EACH edge IN graph.getNeighbors(current) DO
            neighbor ← edge.target
            
            IF neighbor IN visited THEN
                CONTINUE
            END IF
            
            edge_distance ← similarity_to_distance(edge.similarity)
            tentative_g ← current_g + edge_distance
            
            IF neighbor NOT IN g_score OR tentative_g < g_score[neighbor] THEN
                previous[neighbor] ← current
                g_score[neighbor] ← tentative_g
                f_score[neighbor] ← tentative_g + heuristic(neighbor, goal)
                heap.insert((f_score[neighbor], tentative_g, neighbor))
            END IF
        END FOR
    END WHILE
    
    RETURN NULL  // path not found
END
```

**پیچیدگی:**
- زمان: O((V + E) log V) در بدترین حالت
- فضا: O(V)
- **نکته:** با heuristic خوب، تعداد گره‌های بررسی شده کمتر از Dijkstra است.
- 
<div style="page-break-after: always;"></div>

### ۷.۴ الگوریتم Hybrid Search
![[111111111111/algo/phase_1/imgs/image (3).png]]

```
ALGORITHM HybridSearch(graph, start, goal, bfs_depth_limit, min_similarity)
INPUT:
    graph: گراف معنایی
    start: گره مبدأ
    goal: گره مقصد
    bfs_depth_limit: حداکثر عمق برای BFS
    min_similarity: حداقل شباهت

OUTPUT: مسیر از start به goal یا NULL

BEGIN
    // step 1: BFS phase
    bfs_result ← SemanticBFS(graph, start, goal, min_similarity)
    
    IF bfs_result == NULL THEN
        RETURN NULL
    END IF
    
    // if BFS path is short enough, return it directly
    IF bfs_result.path_length ≤ bfs_depth_limit THEN
        RETURN bfs_result
    END IF
    
    // step 2: Dijkstra for optimization
    dijkstra_result ← SemanticDijkstra(graph, start, goal)
    
    IF dijkstra_result == NULL THEN
        RETURN bfs_result
    END IF
    
    // choose the better of the two results
    IF dijkstra_result.path_length < bfs_result.path_length OR
       (dijkstra_result.path_length == bfs_result.path_length AND
        dijkstra_result.total_similarity > bfs_result.total_similarity) THEN
        RETURN dijkstra_result
    END IF
    
    RETURN bfs_result
END
```

**پیچیدگی:**
- زمان: O(V + E) + O((V + E) log V) = O((V + E) log V) در بدترین حالت
- فضا: O(V)

<div style="page-break-after: always;"></div>