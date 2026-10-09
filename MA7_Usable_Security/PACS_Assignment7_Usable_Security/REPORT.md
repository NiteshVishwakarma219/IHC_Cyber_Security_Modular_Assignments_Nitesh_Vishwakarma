# LinkCheck: A Usable Security Nudge for Safer Link Decisions

**Course:** IHC — Practical Approach to Cyber Security  
**Assignment:** 7 — Usable Security: Design Principles  
**Prototype:** LinkCheck  
**Evaluation method:** Heuristic evaluation and reasoned analysis  
**Important:** No user study is claimed. If you run one, add real method and results.

## 1. Problem analysis

People regularly receive links through email, messaging applications, social media, and text messages. A user may click quickly because the message appears urgent, the destination looks familiar, or the user is multitasking. Browser warnings can also become ineffective when they are vague, overly frequent, or do not explain what action the user should take.

The assignment asks for a user-facing security feature that uses behavioral nudging or security notifications to improve security decisions. LinkCheck focuses on the moment before a user opens a link. It reviews simple URL characteristics and presents a concise warning with specific reasons and a deliberate choice to go back or continue after independent verification.

### User need

The user needs to understand *why* a link deserves attention and what to do next, without being overwhelmed by repeated generic alerts.

### Scope

This prototype is a small educational demonstration. It checks basic URL characteristics such as a raw IP address, punycode marker, user-information in a URL, unusually long hostnames, many subdomain levels, suspicious words in a hostname, and HTTP rather than HTTPS. These signals are heuristic only. They cannot determine whether a website is genuinely malicious, and a benign site may trigger a warning.

## 2. Design solution

LinkCheck is a local Flask web prototype with a URL input, a “Review link” action, an explanation panel, and “Go back” / “I verified it — continue” choices. The prototype does not automatically navigate to the supplied URL, avoiding accidental visits to unknown destinations during the demonstration.

### Notification design

- **Contextual:** It appears after the user asks to review a URL.
- **Specific:** It explains the signals found instead of showing only “dangerous.”
- **Actionable:** It encourages the user to verify the domain and source independently.
- **Proportionate:** A simple “no basic warning signs” state is not presented as proof of safety.
- **Non-coercive:** It offers a safer back-out option without shaming or pressuring the user.
- **Transparent:** The interface states that the checker is a heuristic and not a URL reputation service.

## 3. Usable security principles

### Visibility and feedback
The result is displayed immediately after the review action. The result heading summarizes the outcome, while the list explains the reasons.

### Match between system and real-world language
The interface uses familiar language such as “Pause and verify before opening” rather than technical error codes.

### User control and freedom
The user can choose to go back or continue after independent verification. The prototype does not silently open the URL.

### Error prevention
A just-in-time pause adds a small moment for reconsideration before a link-opening decision. The warning is intended to support, not replace, user judgment.

### Recognition over recall
The reasons and next-step advice appear on the same screen, so the user does not need to remember separate instructions.

### Minimize alert fatigue
The tool is designed to present a result only when the user submits a link for review. It does not repeatedly interrupt the user in the background. Future versions should tune the heuristics and measure false positives before deployment.

### Honest system status
A result with no configured warning signs explicitly says that the check cannot confirm safety. This reduces false confidence.

## 4. Implementation overview

- **Language:** Python
- **Web framework:** Flask
- **UI:** HTML and CSS
- **URL parsing:** Python standard-library URL parser and IP-address validation
- **Detection:** Small transparent heuristic rules; no external reputation or threat-intelligence API is queried.

Run locally using the commands in `README.md`. Use harmless example domains for demonstration and do not visit unknown links. The app only displays its analysis; it does not fetch or open the entered destination.

## 5. Evaluation: heuristic review

This report uses a reasoned heuristic evaluation, not a completed user study. The table records expected behavior based on the interface and code. Before submission, execute the scenarios and update the “observed result” column with what actually happened.

| Scenario | Expected behavior | Usability/security rationale |
|---|---|---|
| User enters `https://example.com` | “No basic warning signs detected” with an explicit limitation | Avoids claiming that a heuristic proves safety |
| User enters a raw IP address such as `http://192.0.2.10/login` | Caution result explaining the raw IP signal and HTTP | Gives a concrete reason for pausing |
| User enters a URL with `user@host` pattern | Caution result notes that user-information can disguise the destination | Helps users notice misleading URL structure |
| User enters a hostname with a punycode marker | Caution result asks the user to check for look-alike characters | Makes a subtle visual risk explicit |
| User selects “Go back” | A confirmation explains that not continuing is a safe option when uncertain | Supports user control |
| User selects “I verified it — continue” | The UI records the choice in the result but does not navigate | Avoids accidental external navigation during testing |

### Evaluation findings and limitations

Strengths:
1. The warning is contextual and close to the decision point.
2. Reasons are written in plain language.
3. The interface provides an obvious safer option.
4. The limitations of the heuristic are disclosed.

Limitations:
1. Heuristic rules can produce false positives and false negatives.
2. The prototype has no reputation feed and cannot identify all phishing sites.
3. No participant study or real-world effectiveness test has been performed.
4. The continue action is illustrative; the app does not open a destination.
5. The classroom secret key is hard-coded for local demonstration; do not deploy publicly without changing configuration and adding production security controls.

### Suggested small user study (only if actually performed)

Ask 3–5 volunteers to review a set of harmless example URLs and describe what they would do. Record task completion, whether they understand each warning, their chosen action, and confusion points. Obtain consent, do not show real malicious sites, and report actual observations without inventing results. If no study is conducted, submit the heuristic evaluation above and clearly state that it is literature-/reasoning-based.

## 6. Conclusion

LinkCheck demonstrates a just-in-time security nudge that explains basic warning signals, offers a deliberate choice, and avoids claiming certainty. It applies usable security principles by using clear language, actionable feedback, user control, error prevention, and restrained notifications. The prototype is an educational example rather than a reliable phishing detector. A future version should combine validated reputation data, careful privacy controls, false-positive measurement, accessibility testing, and a real user evaluation.

## 7. References

1. Nielsen Norman Group, “10 Usability Heuristics for User Interface Design”: https://www.nngroup.com/articles/ten-usability-heuristics/
2. OWASP, “Phishing”: https://owasp.org/www-community/attacks/Phishing
3. CISA, “Recognize and Report Phishing”: https://www.cisa.gov/secure-our-world/recognize-and-report-phishing
4. PhishTank, phishing data and community site: https://phishtank.org/
5. Cranor, L. F. (2008), “A Framework for Reasoning About the Human in the Loop,” in *Usable Security* research literature. Verify the exact bibliographic details if citing a specific paper in your final submission.
6. IHC — Practical Approach to Cyber Security, Assignment 7 brief supplied with this project.
