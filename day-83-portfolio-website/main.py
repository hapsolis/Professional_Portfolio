from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os



# Load environment variables from .env file (secret key, email credentials)
load_dotenv()  # Load .env variables

app = Flask(__name__)
# Secret key is required for secure sessions, flash messages, and CSRF protection
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')


# Flask-Mail configuration – uses Gmail SMTP to send real emails from the contact form
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('GMAIL_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_PASSWORD')

mail = Mail(app)



@app.route('/')
def home():
    """
        Renders the main portfolio homepage (index.html).

        This is the entry point of the application.
        - Serves as the landing page with hero, about, stats, skills, resume,
          portfolio preview, certifications grid, and contact form.
        - No dynamic data is passed — all content is static or loaded via Jinja.
        - The sidebar navigation is visible here (controlled via base.html block).

        Related:
        - Links to /portfolio-details and /cert-details are generated in the template.
        - Contact form POSTs to /contact route.
        """
    return render_template('index.html')


@app.route('/portfolio-details')
def portfolio_details():
    """
        Renders a detailed view of a specific portfolio project.

        How it works:
        - Gets the 'project' parameter from the URL query string (?project=...)
        - Uses conditional logic (if/elif) to select the correct project data.
        - Each project passes a large dictionary of context variables to the
          portfolio-details.html template (title, description, images, features, etc.).
        - If no matching project is found → returns 404 "Project not found".

        Purpose:
        - Allows users to click a project card on the homepage and see full details,
          including images, YouTube embeds, feature lists, tools/languages used.

        Related:
        - Called from index.html portfolio section links (e.g. /portfolio-details?project=tia-hydro)
        - Uses the same portfolio-details.html template for all projects.
        """
    project = request.args.get('project')

    # Defaults for non-backwash projects
    images_common = []
    wonderware_images = []
    easybuilder_images = []
    advancedhmi_images = []
    wonderware_video = ""
    easybuilder_video = ""
    advancedhmi_video = ""

    if project == 'tia-hydro':
        return render_template('portfolio-details.html',
                               project=project,  # Pass project name for conditional
                               title="Hydroelectric Plant Simulation – TIA Portal",
                               category="PLC & Automation",
                               description_short="An advanced PLC automation project simulating real-world conditions to manage a hydroelectric plant. It features river flow emulation, interactions between actuators and environmental conditions, mode-based operation, precise PID control, and an intuitive HMI for real-time monitoring and adjustments.",
                               youtube_url="https://www.youtube.com/embed/LUe33eS52jE",
                               images=[
                                   "assets/img/projects/tia-hydro/detail-1.jpg",
                                   "assets/img/projects/tia-hydro/detail-2.jpg",
                                   "assets/img/projects/tia-hydro/detail-3.jpg",
                                   "assets/img/projects/tia-hydro/detail-4.jpg",
                                   "assets/img/projects/tia-hydro/detail-5.jpg",
                                   "assets/img/projects/tia-hydro/detail-6.png",
                                   "assets/img/projects/tia-hydro/detail-7.png",
                                   "assets/img/projects/tia-hydro/detail-8.png"
                               ],
                               features=[
                                   "Multi-language PLC programming using LAD, FBD, SCL, STL, and SFC for dynamic control.",
                                   "Sequential Function Chart (SFC) for managing operational modes (Idle, Warmup, Stabilize, Generation, Cooldown).",
                                   "Interactive HMI with advanced navigation, including dropdown lists for switching between Setpoints and Trends screens.",
                                   "PID Compact Blocks for precise analog device tuning and process optimization.",
                                   "Configurable alarms for real-time fault detection and safety management.",
                                   "Data Acquisition for Performance Analysis: Logs key process data to TXT files for real-time tracking and historical review.",
                                   "Simulation logic emulating real-world dynamics: river flow, baffle regulation, generator RPM/power, lubrication/cooling systems."
                               ],
                               tools="Siemens TIA Portal",
                               languages="LAD, FBD, SCL, STL, SFC",
                               technologies="PID Compact, HMI Design, Alarm Management, Data Logging, Sequential Control",
                               images_common=images_common,  # Defaults
                               wonderware_images=wonderware_images,
                               easybuilder_images=easybuilder_images,
                               advancedhmi_images=advancedhmi_images,
                               wonderware_video=wonderware_video,
                               easybuilder_video=easybuilder_video,
                               advancedhmi_video=advancedhmi_video)

    elif project == 'abb-multi':
        return render_template('portfolio-details.html',
                               project=project,
                               title="Multi-Paradigm Tank Control System – ABB Automation Builder",
                               category="PLC & Automation",
                               description_short="A fully integrated tank control system using all five IEC 61131-3 programming languages (plus Continuous Function Chart) featuring real-time simulation, mode-based control, and advanced alarm handling. Designed in ABB Automation Builder, it demonstrates dynamic level and temperature management with centralized monitoring.",
                               youtube_url="https://www.youtube.com/embed/hp73eRSLGUw",
                               images=[
                                   "assets/img/projects/abb-multi-language/detail-1.png",
                                   "assets/img/projects/abb-multi-language/detail-2.png"
                               ],
                               features=[
                                   "Comprehensive use of all IEC 61131-3 languages: LAD (Offline), FBD (Initialize), ST (Startup), CFC (Operation), IL (Stability) + Continuous Function Chart.",
                                   "Core operational modes with clear separation of logic for safe and efficient transitions.",
                                   "Complementary modules: HOA control, alarm handling, I/O management.",
                                   "Overview POU for real-time visualization and interaction with main variables.",
                                   "Dynamic simulation logic to emulate process conditions and stability mechanisms.",
                                   "Alarm handling with priority evaluation and stability overrides.",
                                   "Modular architecture for easier debugging, scalability, and maintenance."
                               ],
                               tools="ABB Automation Builder",
                               languages="LAD, FBD, ST, CFC, IL, Continuous Function Chart",
                               technologies="Multi-Language Integration, Alarm Handling, Simulation Logic, Modular Design",
                               images_common=images_common,
                               wonderware_images=wonderware_images,
                               easybuilder_images=easybuilder_images,
                               advancedhmi_images=advancedhmi_images,
                               wonderware_video=wonderware_video,
                               easybuilder_video=easybuilder_video,
                               advancedhmi_video=advancedhmi_video)

    elif project == 'backwash-system':
        return render_template('portfolio-details.html',
                               project=project,
                               title="Advanced PLC-Based Filtration & Backwash System with Multi-Platform HMI/SCADA",
                               category="PLC & Automation",
                               description_short="Fully automated industrial filtration system controlled by PLC, with multi-platform HMI/SCADA interfaces (Wonderware, EZware-EasyBuilder, AdvancedHMI), real-time monitoring, automatic backwash, and SQL-based data acquisition.",
                               youtube_url="https://www.youtube.com/embed/FR82vrgv3To",  # main logic video
                               images=[
                                   ""  # Empty for backwash - no single carousel
                               ],
                               features=[
                                   "Advanced PLC logic for automated process control and system interlocks",
                                   "SCADA & HMI development across multiple platforms",
                                   "Real-time data acquisition and SQL-based historical logging",
                                   "Industrial communication using OPC, virtual COM ports, and DF1 protocol"
                               ],
                               tools="RSLogix 500, RSLinx Classic, com0com",
                               languages="Ladder Logic (RSLogix 500)",
                               technologies="OPC Communication, SQL Logging, HMI/SCADA Integration, Sensor Monitoring",
                               images_common=["assets/img/projects/backwash-system/main.jpg"],
                               wonderware_images=[
                                   "assets/img/projects/backwash-system/wonderware/detail-1.jpg",
                                   "assets/img/projects/backwash-system/wonderware/detail-2.jpg",
                                   "assets/img/projects/backwash-system/wonderware/detail-3.jpg",
                                   "assets/img/projects/backwash-system/wonderware/detail-4.jpg",
                                   "assets/img/projects/backwash-system/wonderware/detail-5.jpg",
                                   "assets/img/projects/backwash-system/wonderware/detail-6.png",
                                   "assets/img/projects/backwash-system/wonderware/detail-7.jpg"
                               ],
                               easybuilder_images=[
                                   "assets/img/projects/backwash-system/easybuilder/detail-1.jpg",
                                   "assets/img/projects/backwash-system/easybuilder/detail-2.jpg",
                                   "assets/img/projects/backwash-system/easybuilder/detail-3.jpg",
                                   "assets/img/projects/backwash-system/easybuilder/detail-4.jpg",
                                   "assets/img/projects/backwash-system/easybuilder/detail-5.jpg",
                                   "assets/img/projects/backwash-system/easybuilder/detail-6.jpg"
                               ],
                               advancedhmi_images=[
                                   "assets/img/projects/backwash-system/advanced-hmi/main.jpg"
                               ],
                               wonderware_video="https://www.youtube.com/embed/jZTxJmDKhbY",
                               easybuilder_video="https://www.youtube.com/embed/uydfGAW9IDI",
                               advancedhmi_video="https://www.youtube.com/embed/br4E_7IDrZA")

    else:
        return "Project not found", 404




@app.route('/logic-details')
def logic_details():
    """
        Renders a dedicated explanation page for the logic behind the Backwash Filtration System.

        Purpose:
        - Provides users with a focused, in-depth look at the RSLogix 500 logic and simulation
          of the "Advanced Filtration & Backwash System" project.
        - Displays a main YouTube simulation video, P&ID breakdown, mode explanations
          (Normal Filtration vs Backwash), and instrument/valve details.
        - Acts as a "deep dive" companion page linked from the project detail view.

        How it works:
        - Static route — no query parameters or dynamic data needed.
        - Simply renders logic-details.html with no context variables passed.
        - The template handles all content: embedded YouTube iframe, text explanations,
          and a "Back to Project Details" link.
        """
    return render_template('logic-details.html')




@app.route('/assets/<path:filename>')
def assets(filename):
    """
        Serves static files from the 'assets' folder (images, CSS, JS, fonts, etc.).

        This is a custom static file handler.
        - Allows Flask to serve files like /assets/img/projects/tia-hydro/detail-1.jpg
        - Prevents needing to use url_for('static', filename=...) in every template.

        Security note: <path:filename> allows subdirectories (e.g. assets/img/...).

        Related:
        - Used heavily in all templates for images, CSS, vendor files.
        """
    return send_from_directory('assets', filename)


@app.route('/cert-details')
def cert_details():
    """
        Renders a detailed view of a specific certification/course.

        How it works:
        - Gets the 'course' parameter from the URL (?course=...)
        - Uses if/elif chain to match the course and pass detailed context:
          title, short/long description, images, features list, duration, instructor, link.
        - Special case for 'comm-protocols': passes a list of protocol dictionaries
          (used to render a grid of protocol cards with images/links).
        - If no match → returns 404 "Certification not found".

        Purpose:
        - Lets users click a certification card on the homepage and see full details.

        Related:
        - Called from index.html certifications section (e.g. /cert-details?course=tia-portal)
        - Uses cert-details.html template for all courses.
        """
    course = request.args.get('course')

    if course == 'tia-portal':
        return render_template('cert-details.html',
                               title="TIA Portal Master Project (Level 5)",
                               description_short="Advanced Siemens TIA Portal mastery: full multi-language IEC 61131-3 programming, WinCC RT HMI development, PID control, alarm management, multi-mode state machines, and complete hydroelectric power plant simulation with realistic dynamic process modeling.",
                               description_long="""This Udemy course by Paul Lynn (PLC Dojo) delivered comprehensive, real-world training in Siemens TIA Portal, taking me from advanced concepts to building a fully functional industrial-grade automation system. The core project was a detailed hydroelectric power plant simulation that integrated river flow dynamics, baffle regulation, generator RPM/power output, lubrication/cooling systems, and VFD-controlled oil pumps — all managed with real-time PID loops, fault-tolerant alarm strategies, stability mode recovery, and a complete WinCC RT HMI interface. The focus was on system-level thinking, protective logic, modular architecture, and industrial best practices, equipping me to design, implement, and troubleshoot complex automation solutions in demanding environments.""",
                               images=["assets/img/courses/plc-programming/tia-portal.png"],
                               features=[
                                   "Integrated all IEC 61131-3 languages (LAD, FBD, SCL, STL, GRAPH) + CFC within a single project",
                                   "Built a full hydroelectric plant simulation with river flow, baffle regulation, generator RPM/kW, lubrication/cooling, and VFD oil pump control",
                                   "Implemented multi-mode state machine with safe transitions and interlocks",
                                   "Advanced PID loops for precise RPM stabilization and temperature regulation",
                                   "Professional multi-level alarm system with stability mode, setpoint capture/restore, and audible alerts",
                                   "Complete WinCC RT HMI with dropdown navigation, trends, operator controls, and real-time process visualization",
                                   "Analog scaling, custom function blocks, engineering unit conversion, and realistic process response modeling"
                               ],
                               duration="30 hours",
                               instructor="Paul Lynn (PLC Dojo)",
                               verification_link="https://www.plcdojo.com/certificates/e0bexp1vra")

    elif course == 'hmi-scada':
        return render_template('cert-details.html',
                               title="HMI & SCADA Development",
                               description_short="Multi-platform HMI/SCADA design and implementation across AdvancedHMI, EZware-EasyBuilder 5000, Wonderware, and FactoryTalk — focused on intuitive interfaces, real-time monitoring, alarm handling, trends, data acquisition, and live PLC integration.",
                               description_long="""This course developed my expertise in creating professional-grade visualization and supervisory systems for industrial processes. I designed and programmed complete HMI/SCADA projects with features such as HOA (Hand-Off-Auto) controls, multi-level alarm management, real-time trend analysis, historical data logging, user security levels, and direct communication with live PLC simulations in RSLogix 500. The training emphasized user-centered interface design, performance optimization, fault visualization, and seamless integration with control logic — skills directly applicable to modern industrial operator stations, SCADA systems, and process monitoring applications.""",
                               images=["assets/img/courses/plc-programming/process-visualization.png"],
                               features=[
                                   "Developed full HMI/SCADA projects in AdvancedHMI, EZware-EasyBuilder 5000, Wonderware, and FactoryTalk",
                                   "Implemented HOA controls, multi-level alarms, real-time trends, and historical data acquisition",
                                   "Integrated live PLC simulation (RSLogix 500) for real-time process visualization and control",
                                   "Designed user security levels, intuitive navigation, and operator-friendly interfaces",
                                   "Focused on performance optimization, fault visualization, and seamless control logic integration"
                               ],
                               duration="17 hours",
                               instructor="Paul Lynn (PLC Dojo)",
                               verification_link="https://www.plcdojo.com/certificates/c22rl9pdti")

    elif course == 'iec-paradigms':
        return render_template('cert-details.html',
                               title="IEC Multi-Paradigm Programming",
                               description_short="Advanced application of all five IEC 61131-3 languages plus CFC across multiple platforms — ABB Automation Builder, Connected Components Workbench, and RSLogix 5000 — with focus on modular design, alarms, HOA controls, and dynamic simulations.",
                               description_long="""This course strengthened my versatility in PLC programming by requiring the use of every IEC 61131-3 language (plus CFC) within real projects. I built modular, maintainable solutions including alarm handling, HOA controls, stability overrides, and dynamic process simulations, demonstrating the ability to select the right language for each task while maintaining clean, scalable architecture across different development environments.""",
                               images=["assets/img/courses/plc-programming/iec-paradigms.png"],
                               features=[
                                   "Used all five IEC 61131-3 languages + CFC in real automation projects",
                                   "Developed modular alarm systems, HOA controls, and stability mode logic",
                                   "Created dynamic simulations and real-time process handling",
                                   "Applied best practices for clean, scalable code across platforms",
                                   "Demonstrated language selection based on task requirements"
                               ],
                               duration="16 hours",
                               instructor="Paul Lynn (PLC Dojo)",
                               verification_link="https://www.plcdojo.com/certificates/2hctmrzrku")

    elif course == 'plc-fundamentals':
        return render_template('cert-details.html',
                               title="PLC Programming Fundamentals",
                               description_short="Core foundation in ladder logic programming: digital/analog signals, basic instructions, timers/counters, I/O handling, and creation/troubleshooting of live PLC programs from scratch.",
                               description_long="""This foundational course established my core PLC programming skills using ladder logic — the most widely used language in industrial automation. Through hands-on projects, I learned to interpret specifications, build reliable logic, handle I/O, use timers/counters, and troubleshoot programs in real time, forming the essential base for all subsequent advanced automation work.""",
                               images=["assets/img/courses/plc-programming/plc-fundamentals.png"],
                               features=[
                                   "Mastered ladder logic (LAD) — the primary industrial PLC language",
                                   "Learned digital and analog signal handling and I/O configuration",
                                   "Implemented timers, counters, and basic control instructions",
                                   "Built and troubleshot complete live PLC programs",
                                   "Developed foundational skills for reading and writing industrial logic"
                               ],
                               duration="25.5 hours",
                               instructor="Paul Lynn (PLC Dojo)",
                               verification_link="https://www.plcdojo.com/certificates/jbc4bgcaye")

    elif course == 'applied-logic':
        return render_template('cert-details.html',
                               title="Applied Logic – PLC Problem Solving",
                               description_short="Intensive problem-solving course: independent design and troubleshooting of complex ladder logic solutions based on detailed industrial specifications and real-world automation challenges.",
                               description_long="""This course pushed my logical thinking and debugging skills to the next level by presenting progressively harder real-world automation problems. I had to develop complete solutions unassisted, following strict specifications — training me to think like an industrial programmer who can deliver reliable, efficient logic under pressure without hand-holding.""",
                               images=["assets/img/courses/plc-programming/applied-logic.png"],
                               features=[
                                   "Solved complex industrial automation problems independently",
                                   "Designed ladder logic following detailed technical specifications",
                                   "Developed strong debugging and troubleshooting methodology",
                                   "Built reliable, production-ready control logic",
                                   "Trained to deliver solutions under real-world constraints"
                               ],
                               duration="8.5 hours",
                               instructor="Paul Lynn (PLC Dojo)",
                               verification_link="https://www.plcdojo.com/certificates/kqiih0klpz")

    elif course == 'vfd-drives':
        return render_template('cert-details.html',
                               title="Variable Frequency Drives (VFD) Configuration",
                               description_short="In-depth configuration, tuning, and troubleshooting of VFDs from leading brands (Danfoss, Yaskawa, Delta, HNC, PowerFlex 525) — including motor theory, wiring, control modes, and integration with Allen-Bradley PLCs.",
                               description_long="""This course gave me practical, brand-specific expertise in VFD drives — from parameter setup and tuning to advanced control modes (SVC, V/Hz, DTC) and seamless integration with Allen-Bradley PLCs using Connected Components Workbench and Studio 5000. I gained a strong understanding of induction motor behavior, drive wiring, fault diagnosis, and optimization for industrial applications.""",
                               images=["assets/img/courses/vfd.png"],
                               features=[
                                   "Configured and tuned VFDs from Danfoss, Yaskawa, Delta, HNC, and PowerFlex 525",
                                   "Mastered control modes: SVC, V/Hz, and DTC",
                                   "Understood induction motor theory and drive wiring best practices",
                                   "Integrated VFDs with Allen-Bradley PLCs using CCW and Studio 5000",
                                   "Learned fault diagnosis, parameter optimization, and performance tuning"
                               ],
                               duration="17 hours",
                               instructor="Rodrigo Diaz (PLC Academy)",
                               verification_link="https://www.udemy.com/certificate/UC-88ec908f-e764-43bd-aef7-13d31ee9d5e6/")



    elif course == 'comm-protocols':
        return render_template('cert-details.html',
                               title="Industrial Communication Protocols",
                               description_short="Deep knowledge of key industrial protocols: Modbus RTU/TCP, Ethernet/IP, BACnet, DNP3, Profibus DP — essential for device integration, networking, and reliable data exchange in automation systems.",
                               description_long="This training provided comprehensive understanding of the most widely used communication protocols in industrial automation. Each protocol was studied in depth, including its physical layer, data model, message structure, addressing, function codes, and practical application in real systems. The focus was on integration challenges, network design considerations, troubleshooting techniques, and how these protocols enable seamless interoperability between PLCs, HMIs, sensors, actuators, and SCADA systems.",
                               images=[],  # No single main image — we'll use grid below
                               features=[
                                   "Mastered Modbus RTU, Modbus TCP/IP, Ethernet/IP, BACnet, DNP3, and Profibus DP",
                                   "Understood protocol layers, addressing, function codes, and data formats",
                                   "Learned network topology, cabling, and integration best practices",
                                   "Developed troubleshooting skills for communication faults",
                                   "Explored real-world applications in PLC-HMI-SCADA systems"
                               ],
                               duration="14 hours",
                               instructor="Emile Ackbarali (PLC Dojo)",
                               verification_link="",
                               # Pass the 6 protocols as a list for the grid
                               protocols=[
                                   {
                                       "name": "BACnet",
                                       "image": "assets/img/courses/communication-protocols/bacnet.png",
                                       "link": "https://www.plcdojo.com/certificates/9pdfkywkcd"
                                   },
                                   {
                                       "name": "DNP3",
                                       "image": "assets/img/courses/communication-protocols/dnp3.png",
                                       "link": "https://www.plcdojo.com/certificates/m5ejaslvdq"
                                   },
                                   {
                                       "name": "Ethernet/IP",
                                       "image": "assets/img/courses/communication-protocols/ethernet-ip.png",
                                       "link": "https://www.plcdojo.com/certificates/kbk8xjdihp"
                                   },
                                   {
                                       "name": "Modbus RTU/RS-485",
                                       "image": "assets/img/courses/communication-protocols/modbug-rs485.png",
                                       "link": "https://www.plcdojo.com/certificates/gi2c3aqjea"
                                   },
                                   {
                                       "name": "Modbus TCP/IP",
                                       "image": "assets/img/courses/communication-protocols/modbus-tcp-ip.png",
                                       "link": "https://www.plcdojo.com/certificates/guwptv1evm"
                                   },
                                   {
                                       "name": "Profibus DP",
                                       "image": "assets/img/courses/communication-protocols/profibus-dp.png",
                                       "link": "https://www.plcdojo.com/certificates/ka6tssmthc"
                                   }
                               ])



    else:
        return "Certification not found", 404



@app.route('/contact', methods=['POST'])
def contact():
    """
        Handles POST requests from the contact form on the homepage.

        Workflow:
        1. Extracts form data: name, email, subject (optional), message.
        2. Validates required fields (name + email).
        3. Builds a clean, styled HTML email body with sender info + user message.
        4. Sends email via Flask-Mail (to yourself) with both plain text fallback and HTML version.
        5. On success: flashes green success message.
        6. On failure (SMTP error, etc.): flashes red error message with details.
        7. Redirects back to homepage + #contact anchor (so user sees the flash).

        Security:
        - Uses Gmail App Password (never store real password).
        - No user data is stored — only emailed to yourself.

        Related:
        - Form in index.html → action="{{ url_for('contact') }}" method="post"
        - Uses flash() + get_flashed_messages() in template for user feedback.
        """
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject', 'Contact Form Message')
    message_body = request.form.get('message') or "(No message provided)"

    if not name or not email:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('home') + '#contact')

    # Clean and wrap the HTML message
    html_message = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2c3e50;">New Contact Message</h2>
        <p><strong>From:</strong> {name} &lt;{email}&gt;</p>
        <p><strong>Subject:</strong> {subject}</p>
        <hr style="border: 1px solid #eee; margin: 20px 0;">
        <div style="margin: 20px 0;">
          {message_body}
        </div>
        <hr style="border: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 0.9em; color: #777;">
          This message was sent from your portfolio website contact form.
        </p>
      </body>
    </html>
    """

    try:
        msg = Message(
            subject=f"New Portfolio Message: {subject}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']],
            body=f"From: {name} <{email}>\nSubject: {subject}\n\n{message_body}",  # Plain text fallback
            html=html_message  # Rich HTML version
        )
        mail.send(msg)
        flash('Your message has been sent successfully! I will get back to you soon.', 'success')
    except Exception as e:
        flash(f'Error sending message: {str(e)}', 'danger')

    return redirect(url_for('home') + '#contact')










if __name__ == '__main__':
    """
        Entry point of the Flask application.

        - Runs the development server on port 5000 with debug mode enabled.
        - Debug=True enables auto-reload and detailed error pages 
        """
    app.run(debug=True, port=5000)