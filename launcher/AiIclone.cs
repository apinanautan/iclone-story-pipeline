// Ai-iclone.exe: tiny launcher next to scripts/. Build: powershell -File launcher\build.ps1
//   From a terminal (AI or person): Ai-iclone.exe [args]  = py -3 scripts\ai_iclone.py [args]  (text, same output)
//   Double-click in Explorer:        opens the Ai-iclone window (scripts\progress_app.py)
// The scripts stay plain Python so they can be fixed without rebuilding this exe.
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

[assembly: System.Reflection.AssemblyTitle("Ai-iclone")]
[assembly: System.Reflection.AssemblyProduct("Ai-iclone")]

static class AiIclone
{
    [DllImport("kernel32.dll")] static extern uint GetConsoleProcessList(uint[] list, uint count);
    [DllImport("kernel32.dll")] static extern bool SetConsoleOutputCP(uint cp);

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

    static int Main(string[] args)
    {
        string root = AppDomain.CurrentDomain.BaseDirectory;
        string script = Path.Combine(root, "scripts", "ai_iclone.py");
        if (!File.Exists(script))
        {
            Console.Error.WriteLine("Ai-iclone: scripts\\ai_iclone.py not found next to this exe (" + root + ")");
            return 1;
        }
        // double-clicked = this exe owns its console alone -> open the window instead of a flashing console
        // (an AI's tool captures stdout -> redirected -> always text, never the window)
        bool doubleClicked = args.Length == 0 && !Console.IsOutputRedirected && GetConsoleProcessList(new uint[2], 2) == 1;
        if (doubleClicked || (args.Length > 0 && args[0].Equals("window", StringComparison.OrdinalIgnoreCase)))
        {
            var w = new ProcessStartInfo("pyw", "-3 " + Quote(Path.Combine(root, "scripts", "progress_app.py")))
            { UseShellExecute = false, WorkingDirectory = root, CreateNoWindow = true };
            try { Process.Start(w); return 0; }
            catch (Exception e) { Console.Error.WriteLine("Ai-iclone: cannot start pyw (Python 3 launcher): " + e.Message); return 1; }
        }
        SetConsoleOutputCP(65001);
        var sbArgs = new StringBuilder("-3 " + Quote(script));
        foreach (var a in args) sbArgs.Append(' ').Append(Quote(a));
        var psi = new ProcessStartInfo("py", sbArgs.ToString()) { UseShellExecute = false, WorkingDirectory = root };
        psi.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
        psi.EnvironmentVariables["AI_ICLONE_EXE"] = Path.Combine(root, "Ai-iclone.exe");
        try
        {
            using (var p = Process.Start(psi)) { p.WaitForExit(); return p.ExitCode; }
        }
        catch (Exception e) { Console.Error.WriteLine("Ai-iclone: cannot start py (Python 3 launcher): " + e.Message); return 1; }
    }
}
