using System;
using System.Runtime.InteropServices;
namespace IG {
public class U {
[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c);
[DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h,out RECT r);
[DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")] public static extern void mouse_event(int f,int x,int y,int d,int e);
[DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr h,int m,IntPtr w,string l);
[DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h,int m,IntPtr w,IntPtr l);
[DllImport("user32.dll")] public static extern void keybd_event(byte vk,byte sc,int f,int e);
[DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
[DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern IntPtr LoadKeyboardLayout(string id,uint f);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr w,out uint p);
[DllImport("user32.dll",EntryPoint="GetWindowThreadProcessId")] public static extern uint ThreadOf(IntPtr w,IntPtr p);
[DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
[DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a,uint b,bool f);
[DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
public struct RECT{public int L,T,R,B;}
}
public class E {
public delegate bool EnumProc(IntPtr h,IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc e,IntPtr l);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr w,out uint p);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr w);
}
}
