// Ai-iclone.exe: one file, no unzip. Build: powershell -File launcher\build.ps1
//   From a terminal (AI or person): Ai-iclone.exe [args]  = py -3 scripts\ai_iclone.py [args]  (text)
//   Double-click in Explorer:        opens the Ai-iclone window (scripts\progress_app.py)
//   Ai-iclone.exe update            check GitHub for a newer release now
//
// Where the program files live (APP):
//   - the exe's own folder if it has scripts\ai_iclone.py (a git checkout or an unzipped release)
//   - otherwise %LOCALAPPDATA%\Ai-iclone  (first run downloads the latest release there by itself)
// Updates: at most every 10 minutes the exe reads the latest GitHub release tag; if it is newer than APP\VERSION
// it downloads that release and copies it over APP. Never touched: work data (stories\, parts\, progress\
// except new template files) and paths.local.json. A git checkout is never auto-updated (use git pull).
using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.RegularExpressions;

[assembly: System.Reflection.AssemblyTitle("Ai-iclone")]
[assembly: System.Reflection.AssemblyProduct("Ai-iclone")]

static class AiIclone
{
    const string REPO = "apinanautan/iclone-story-pipeline";
    static readonly string[] KEEP_DIRS = { "stories", "parts", "progress" };   // work data: only add missing files
    static readonly string[] KEEP_FILES = { "paths.local.json" };

    [DllImport("kernel32.dll")] static extern uint GetConsoleProcessList(uint[] list, uint count);
    [DllImport("kernel32.dll")] static extern bool SetConsoleOutputCP(uint cp);

    static void Log(string s) { Console.Error.WriteLine("Ai-iclone: " + s); }

    static string Quote(string a)
    {
        if (a.Length > 0 && a.IndexOfAny(new[] { ' ', '\t', '"' }) < 0) return a;
        var sb = new StringBuilder("\"");
        int bs = 0;
        foreach (char c in a)
        {
            if (c == '\\') { bs++; continue; }
            if (c == '"') { sb.Append('\\', bs * 2 + 1); sb.Append('"'); bs = 0; continue; }
            sb.Append('\\', bs); bs = 0; sb.Append(c);
        }
        sb.Append('\\', bs * 2);
        return sb.Append('"').ToString();
    }

    static string ReadVersion(string app)
    {
        try { return File.ReadAllText(Path.Combine(app, "VERSION")).Trim(); } catch { return ""; }
    }

    static int[] Ver(string v)
    {
        var m = Regex.Matches(v ?? "", @"\d+"); var r = new int[3];
        for (int i = 0; i < 3 && i < m.Count; i++) r[i] = int.Parse(m[i].Value);
        return r;
    }

    static bool Newer(string a, string b)   // a > b
    {
        int[] x = Ver(a), y = Ver(b);
        for (int i = 0; i < 3; i++) if (x[i] != y[i]) return x[i] > y[i];
        return false;
    }

    static WebClient Web()
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        var w = new WebClient();
        w.Headers[HttpRequestHeader.UserAgent] = "Ai-iclone";
        return w;
    }

    static string LatestTag()
    {
        using (var w = Web())
        {
            string json = w.DownloadString("https://api.github.com/repos/" + REPO + "/releases/latest");
            var m = Regex.Match(json, "\"tag_name\"\\s*:\\s*\"([^\"]+)\"");
            return m.Success ? m.Groups[1].Value : null;
        }
    }

    static bool Under(string rel, string dir)
    {
        return rel.StartsWith(dir + "\\", StringComparison.OrdinalIgnoreCase) || rel.Equals(dir, StringComparison.OrdinalIgnoreCase);
    }

    static void Install(string tag, string app)
    {
        string tmp = Path.Combine(Path.GetTempPath(), "Ai-iclone-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(tmp);
        try
        {
            string zip = Path.Combine(tmp, "src.zip");
            Log("downloading " + tag + " from GitHub ...");
            using (var w = Web()) w.DownloadFile("https://codeload.github.com/" + REPO + "/zip/refs/tags/" + tag, zip);
            string ex = Path.Combine(tmp, "x");
            ZipFile.ExtractToDirectory(zip, ex);
            string top = Directory.GetDirectories(ex)[0];   // codeload: one top folder <repo>-<version>
            if (!File.Exists(Path.Combine(top, "scripts", "ai_iclone.py"))) throw new Exception("release has no scripts\\ai_iclone.py");
            string self = Process.GetCurrentProcess().MainModule.FileName;
            int n = 0;
            foreach (string f in Directory.GetFiles(top, "*", SearchOption.AllDirectories))
            {
                string rel = f.Substring(top.Length + 1);
                string dst = Path.Combine(app, rel);
                bool keep = Array.Exists(KEEP_FILES, k => rel.Equals(k, StringComparison.OrdinalIgnoreCase))
                            || Array.Exists(KEEP_DIRS, d => Under(rel, d));
                if (keep && File.Exists(dst)) continue;
                Directory.CreateDirectory(Path.GetDirectoryName(dst));
                if (string.Equals(Path.GetFullPath(dst), self, StringComparison.OrdinalIgnoreCase))
                {   // a running exe cannot be overwritten, but it can be renamed
                    string old = self + ".old";
                    try { File.Delete(old); } catch { }
                    File.Move(self, old);
                }
                File.Copy(f, dst, true); n++;
            }
            Log("installed " + tag + " (" + n + " files) -> " + app);
        }
        finally { try { Directory.Delete(tmp, true); } catch { } }
    }

    // returns false only when there is no program at all and it could not be downloaded
    static bool Update(string app, bool force)
    {
        bool have = File.Exists(Path.Combine(app, "scripts", "ai_iclone.py"));
        if (Directory.Exists(Path.Combine(app, ".git")))
        {
            if (force) Log("this folder is a git checkout: update it with git pull (not auto-updated)");
            return have;
        }
        string stamp = Path.Combine(app, "progress", "update_check.txt");
        if (have && !force)
        {
            try { if ((DateTime.UtcNow - File.GetLastWriteTimeUtc(stamp)).TotalMinutes < 10) return true; } catch { }
        }
        try
        {
            string tag = LatestTag();
            Directory.CreateDirectory(Path.GetDirectoryName(stamp));
            File.WriteAllText(stamp, DateTime.Now.ToString("s") + " latest " + tag);
            string cur = ReadVersion(app);
            if (tag != null && (!have || Newer(tag, cur))) { if (have) Log("update " + cur + " -> " + tag); Install(tag, app); }
            else if (force) Log("up to date (" + cur + ")");
        }
        catch (Exception e)
        {
            if (!have) { Log("cannot download the program from GitHub: " + e.Message); return false; }
            if (force) Log("update check failed (offline?): " + e.Message + " - using " + ReadVersion(app));
        }
        return true;
    }

    static int Main(string[] args)
    {
        string exeDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\');
        string app = File.Exists(Path.Combine(exeDir, "scripts", "ai_iclone.py")) ? exeDir
            : !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("AI_ICLONE_HOME")) ? Environment.GetEnvironmentVariable("AI_ICLONE_HOME")
            : Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Ai-iclone");
        bool forceUpdate = args.Length > 0 && args[0].Equals("update", StringComparison.OrdinalIgnoreCase);
        if (!Update(app, forceUpdate)) return 1;
        if (forceUpdate) { Console.WriteLine("Ai-iclone " + ReadVersion(app) + "  (" + app + ")"); return 0; }

        // double-clicked = this exe owns its console alone and nobody reads its output -> open the window
        bool doubleClicked = args.Length == 0 && !Console.IsOutputRedirected && GetConsoleProcessList(new uint[2], 2) == 1;
        if (doubleClicked || (args.Length > 0 && args[0].Equals("window", StringComparison.OrdinalIgnoreCase)))
        {
            var w = new ProcessStartInfo("pyw", "-3 " + Quote(Path.Combine(app, "scripts", "progress_app.py")))
            { UseShellExecute = false, WorkingDirectory = app, CreateNoWindow = true };
            try { Process.Start(w); return 0; }
            catch (Exception e) { Log("cannot start pyw - install Python 3 from python.org (" + e.Message + ")"); return 1; }
        }
        SetConsoleOutputCP(65001);
        var sbArgs = new StringBuilder("-3 " + Quote(Path.Combine(app, "scripts", "ai_iclone.py")));
        foreach (var a in args) sbArgs.Append(' ').Append(Quote(a));
        var psi = new ProcessStartInfo("py", sbArgs.ToString()) { UseShellExecute = false, WorkingDirectory = app };
        psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
        psi.EnvironmentVariables["AI_ICLONE_EXE"] = Process.GetCurrentProcess().MainModule.FileName;
        try
        {
            using (var p = Process.Start(psi)) { p.WaitForExit(); return p.ExitCode; }
        }
        catch (Exception e) { Log("cannot start py - install Python 3 from python.org (" + e.Message + ")"); return 1; }
    }
}
