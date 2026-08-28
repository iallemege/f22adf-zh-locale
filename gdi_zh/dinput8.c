#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <string.h>

#ifndef MB_ERR_INVALID_CHARS
#define MB_ERR_INVALID_CHARS 0x00000008
#endif
#ifndef CP_ACP
#define CP_ACP 0
#endif
#ifndef CP_UTF8
#define CP_UTF8 65001
#endif

int WINAPI MultiByteToWideChar(UINT CodePage, DWORD dwFlags, LPCSTR lpMultiByteStr, int cbMultiByte,
                               LPWSTR lpWideCharStr, int cchWideChar);

typedef HRESULT(WINAPI *DirectInput8Create_t)(HINSTANCE, DWORD, const void *, LPVOID *, LPVOID);
typedef BOOL(WINAPI *ExtTextOutA_t)(HDC, int, int, UINT, const RECT *, LPCSTR, UINT, const INT *);
typedef BOOL(WINAPI *TextOutA_t)(HDC, int, int, LPCSTR, int);
typedef BOOL(WINAPI *GetCharWidth32A_t)(HDC, UINT, UINT, LPINT);
typedef BOOL(WINAPI *GetTextExtentPoint32A_t)(HDC, LPCSTR, int, LPSIZE);
typedef int(WINAPI *DrawTextA_t)(HDC, LPCSTR, int, LPRECT, UINT);

static HMODULE g_dinput;
static DirectInput8Create_t g_DirectInput8Create;
static ExtTextOutA_t pExtTextOutA;
static TextOutA_t pTextOutA;
static GetCharWidth32A_t pGetCharWidth32A;
static GetTextExtentPoint32A_t pGetTextExtentPoint32A;
static DrawTextA_t pDrawTextA;

typedef struct {
    HDC hdc;
    BYTE lead;
    int x, y;
} DcState;

static DcState g_st[16];
static CRITICAL_SECTION g_cs;
static void log_line(const char *s);

static int is_lead(unsigned char b) { return b >= 0x81 && b <= 0xFE; }
static int is_trail(unsigned char b) {
    return (b >= 0x40 && b <= 0x7E) || (b >= 0x80 && b <= 0xFE);
}

static DcState *state_for(HDC hdc) {
    int i, empty = -1;
    for (i = 0; i < 16; i++) {
        if (g_st[i].hdc == hdc)
            return &g_st[i];
        if (g_st[i].hdc == NULL && empty < 0)
            empty = i;
    }
    if (empty < 0)
        empty = 0;
    g_st[empty].hdc = hdc;
    g_st[empty].lead = 0;
    return &g_st[empty];
}

static int has_gbk_pair(const char *s, int n) {
    int i;
    if (!s || n < 2)
        return 0;
    for (i = 0; i < n - 1; i++) {
        unsigned char a = (unsigned char)s[i];
        unsigned char b = (unsigned char)s[i + 1];
        if (is_lead(a) && is_trail(b))
            return 1;
    }
    return 0;
}

static wchar_t *to_wide(UINT cp, LPCSTR s, int n, int *out_n) {
    int wlen;
    wchar_t *w;
    if (!s || n <= 0)
        return NULL;
    wlen = MultiByteToWideChar(cp, MB_ERR_INVALID_CHARS, s, n, NULL, 0);
    if (wlen <= 0)
        return NULL;
    w = (wchar_t *)HeapAlloc(GetProcessHeap(), 0, (wlen + 1) * sizeof(wchar_t));
    if (!w)
        return NULL;
    MultiByteToWideChar(cp, 0, s, n, w, wlen);
    w[wlen] = 0;
    if (out_n)
        *out_n = wlen;
    return w;
}

/* Menu / load-bar labels. Draw-time only so TITLE lookups stay English. UTF-8 bytes. */
static const struct {
    const char *en;
    const char *zh;
} g_ui[] = {
    {"Simulator", "\xE6\xA8\xA1\xE6\x8B\x9F\xE8\xAE\xAD\xE7\xBB\x83"},
    {"Tour of Duty", "\xE6\x88\x98\xE5\x8C\xBA\xE5\xB7\xA1\xE8\x88\xAA"},
    {"Quick Combat", "\xE5\xBF\xAB\xE9\x80\x9F\xE4\xBD\x9C\xE6\x88\x98"},
    {"Multiplay", "\xE5\xA4\x9A\xE4\xBA\xBA\xE6\xB8\xB8\xE6\x88\x8F"},
    {"Multiplayer", "\xE5\xA4\x9A\xE4\xBA\xBA\xE6\xB8\xB8\xE6\x88\x8F"},
    {"Options", "\xE9\x80\x89\xE9\xA1\xB9"},
    {"F-22 Credits", "\xE5\x88\xB6\xE4\xBD\x9C\xE4\xBA\xBA\xE5\x91\x98"},
    {"F22 Credits", "\xE5\x88\xB6\xE4\xBD\x9C\xE4\xBA\xBA\xE5\x91\x98"},
    {"Credits", "\xE5\x88\xB6\xE4\xBD\x9C\xE4\xBA\xBA\xE5\x91\x98"},
    {"Quit", "\xE9\x80\x80\xE5\x87\xBA"},
    {"Help", "\xE5\xB8\xAE\xE5\x8A\xA9"},
    {"F-22 Demo", "\xE6\xBC\x94\xE7\xA4\xBA"},
    {"F22 Demo", "\xE6\xBC\x94\xE7\xA4\xBA"},
    {"LOADING TERRAIN", "\xE8\xBD\xBD\xE5\x85\xA5\xE5\x9C\xB0\xE5\xBD\xA2"},
    {"LOADING WEAPONS", "\xE8\xBD\xBD\xE5\x85\xA5\xE6\xAD\xA6\xE5\x99\xA8"},
    {"LOADING SPEECH", "\xE8\xBD\xBD\xE5\x85\xA5\xE8\xAF\xAD\xE9\x9F\xB3"},
    {"LOADING SFX", "\xE8\xBD\xBD\xE5\x85\xA5\xE9\x9F\xB3\xE6\x95\x88"},
    {"LOADING RECORDING", "\xE8\xBD\xBD\xE5\x85\xA5\xE8\xAE\xB0\xE5\xBD\x95"},
    {"LOADING COCKPIT VOICE", "\xE8\xBD\xBD\xE5\x85\xA5\xE5\xBA\xA7\xE8\x88\xB1\xE8\xAF\xAD\xE9\x9F\xB3"},
    {"LOADING CLOUD LEVELS", "\xE8\xBD\xBD\xE5\x85\xA5\xE4\xBA\x91\xE5\xB1\x82"},
    {" (Loading)", " (\xE8\xBD\xBD\xE5\x85\xA5\xE4\xB8\xAD)"},
    {"OK", "\xE7\xA1\xAE\xE5\xAE\x9A"},
    {"Cancel", "\xE5\x8F\x96\xE6\xB6\x88"},
    {"Accept", "\xE6\x8E\xA5\xE5\x8F\x97"},
    {"Free Flight", "\xE8\x87\xAA\xE7\x94\xB1\xE9\xA3\x9E\xE8\xA1\x8C"},
    {"Flight Training", "\xE9\xA3\x9E\xE8\xA1\x8C\xE8\xAE\xAD\xE7\xBB\x83"},
    {"Flight", "\xE9\xA3\x9E\xE8\xA1\x8C\xE8\xAE\xAD\xE7\xBB\x83"},
    {"Weapons", "\xE6\xAD\xA6\xE5\x99\xA8\xE8\xAE\xAD\xE7\xBB\x83"},
    {"Combat Tactics", "\xE6\x88\x98\xE6\x96\x97\xE6\x88\x98\xE6\x9C\xAF"},
    {"Combat Manouvres", "\xE6\x88\x98\xE6\x96\x97\xE6\x9C\xBA\xE5\x8A\xA8"},
    {"Training Program", "\xE8\xAE\xAD\xE7\xBB\x83\xE5\xA4\xA7\xE7\xBA\xB2"},
    {"Training Missions", "\xE8\xAE\xAD\xE7\xBB\x83\xE4\xBB\xBB\xE5\x8A\xA1"},
    {NULL, NULL},
};

static wchar_t *lookup_ui(LPCSTR str, int n, int *wn) {
    char buf[96];
    char utf[128];
    int i, pre;
    if (!str || n <= 0 || n >= (int)sizeof(buf))
        return NULL;
    memcpy(buf, str, n);
    buf[n] = 0;
    for (i = 0; g_ui[i].en; i++) {
        if (lstrcmpA(buf, g_ui[i].en) == 0)
            return to_wide(CP_UTF8, g_ui[i].zh, lstrlenA(g_ui[i].zh), wn);
    }
    if (n >= 10 && memcmp(buf + n - 10, " - LOADING", 10) == 0) {
        pre = n - 10;
        if (pre > 80)
            return NULL;
        memcpy(utf, buf, pre);
        utf[pre] = 0;
        lstrcatA(utf, " - \xE8\xBD\xBD\xE5\x85\xA5\xE4\xB8\xAD");
        return to_wide(CP_UTF8, utf, lstrlenA(utf), wn);
    }
    return NULL;
}

static void patch_cstr_gbk(BYTE *base, DWORD size, const char *en, const char *gbk) {
    DWORD i;
    size_t lo = lstrlenA(en);
    size_t ln = lstrlenA(gbk);
    DWORD prot;
    if (!base || ln > lo || lo < 4)
        return;
    for (i = 0; i + lo < size; i++) {
        if (base[i] == (BYTE)en[0] && memcmp(base + i, en, lo) == 0 && base[i + lo] == 0) {
            if (VirtualProtect(base + i, (DWORD)(lo + 1), PAGE_EXECUTE_READWRITE, &prot)) {
                memcpy(base + i, gbk, ln + 1);
                VirtualProtect(base + i, (DWORD)(lo + 1), prot, &prot);
            }
        }
    }
}

static void patch_loading_strings(void) {
    BYTE *base = (BYTE *)GetModuleHandleA(NULL);
    IMAGE_NT_HEADERS *nt;
    DWORD size;
    if (!base)
        return;
    nt = (IMAGE_NT_HEADERS *)(base + ((IMAGE_DOS_HEADER *)base)->e_lfanew);
    size = nt->OptionalHeader.SizeOfImage;
    /* GBK, shorter than English. Overlay walker + GDI hook both understand it. */
    patch_cstr_gbk(base, size, "LOADING TERRAIN", "\xD4\xD8\xC8\xEB\xB5\xD8\xD0\xCE");
    patch_cstr_gbk(base, size, "LOADING WEAPONS", "\xD4\xD8\xC8\xEB\xCE\xE4\xC6\xF7");
    patch_cstr_gbk(base, size, "LOADING SPEECH", "\xD4\xD8\xC8\xEB\xD3\xEF\xD2\xF4");
    patch_cstr_gbk(base, size, "LOADING SFX", "\xD4\xD8\xC8\xEB\xD2\xF4\xD0\xA7");
    patch_cstr_gbk(base, size, "LOADING RECORDING", "\xD4\xD8\xC8\xEB\xBC\xC7\xC2\xBC");
    patch_cstr_gbk(base, size, "LOADING COCKPIT VOICE", "\xD4\xD8\xC8\xEB\xD7\xF9\xB2\xD5\xD3\xEF\xD2\xF4");
    patch_cstr_gbk(base, size, "LOADING CLOUD LEVELS", "\xD4\xD8\xC8\xEB\xD4\xC6\xB2\xE3");
    patch_cstr_gbk(base, size, "%s - LOADING", "%s - \xD4\xD8\xC8\xEB\xD6\xD0");
    patch_cstr_gbk(base, size, " (Loading)", " (\xD4\xD8\xC8\xEB\xD6\xD0)");
    log_line("patched loading strings");
}

static BOOL WINAPI H_ExtTextOutA(HDC hdc, int x, int y, UINT opt, const RECT *rc, LPCSTR str, UINT c,
                                 const INT *dx) {
    DcState *st;
    unsigned char b;
    wchar_t wc;
    char pair[2];
    BOOL ok;
    wchar_t *ui;
    int wn;

    if (!str || c == 0)
        return pExtTextOutA(hdc, x, y, opt, rc, str, c, dx);

    ui = lookup_ui(str, (int)c, &wn);
    if (ui) {
        ok = ExtTextOutW(hdc, x, y, opt, rc, ui, (UINT)wn, NULL);
        HeapFree(GetProcessHeap(), 0, ui);
        return ok;
    }

    if (c >= 2 && has_gbk_pair(str, (int)c)) {
        int wn = 0;
        wchar_t *w = to_wide(936, str, (int)c, &wn);
        if (w) {
            ok = ExtTextOutW(hdc, x, y, opt, rc, w, (UINT)wn, NULL);
            HeapFree(GetProcessHeap(), 0, w);
            return ok;
        }
    }

    if (c != 1)
        return pExtTextOutA(hdc, x, y, opt, rc, str, c, dx);

    b = (unsigned char)str[0];
    EnterCriticalSection(&g_cs);
    st = state_for(hdc);

    if (st->lead) {
        if (is_trail(b)) {
            int gx, gy;
            pair[0] = (char)st->lead;
            pair[1] = (char)b;
            gx = st->x;
            gy = st->y;
            st->lead = 0;
            LeaveCriticalSection(&g_cs);
            if (MultiByteToWideChar(936, 0, pair, 2, &wc, 1) == 1)
                return ExtTextOutW(hdc, gx, gy, opt, rc, &wc, 1, NULL);
            return pExtTextOutA(hdc, x, y, opt, rc, str, c, dx);
        }
        st->lead = 0;
    }

    if (is_lead(b)) {
        st->lead = b;
        st->x = x;
        st->y = y;
        LeaveCriticalSection(&g_cs);
        return TRUE;
    }
    LeaveCriticalSection(&g_cs);
    return pExtTextOutA(hdc, x, y, opt, rc, str, c, dx);
}

static BOOL WINAPI H_TextOutA(HDC hdc, int x, int y, LPCSTR str, int c) {
    return H_ExtTextOutA(hdc, x, y, 0, NULL, str, (UINT)(c < 0 ? 0 : c), NULL);
}

static BOOL WINAPI H_GetCharWidth32A(HDC hdc, UINT first, UINT last, LPINT buf) {
    DcState *st;
    unsigned char b;
    char pair[2];
    wchar_t wc;
    INT ww;

    if (!buf)
        return pGetCharWidth32A(hdc, first, last, buf);

    if (first == last && first <= 0xFF) {
        b = (unsigned char)first;
        EnterCriticalSection(&g_cs);
        st = state_for(hdc);
        if (st->lead && is_trail(b)) {
            pair[0] = (char)st->lead;
            pair[1] = (char)b;
            LeaveCriticalSection(&g_cs);
            if (MultiByteToWideChar(936, 0, pair, 2, &wc, 1) == 1 && GetCharWidth32W(hdc, wc, wc, &ww)) {
                *buf = ww;
                return TRUE;
            }
            return pGetCharWidth32A(hdc, first, last, buf);
        }
        if (is_lead(b)) {
            LeaveCriticalSection(&g_cs);
            *buf = 0;
            return TRUE;
        }
        LeaveCriticalSection(&g_cs);
    } else if (last <= 0xFF && buf) {
        BOOL ok = pGetCharWidth32A(hdc, first, last, buf);
        if (ok) {
            UINT i;
            for (i = first; i <= last; i++) {
                if (is_lead((unsigned char)i))
                    buf[i - first] = 0;
            }
        }
        return ok;
    }
    return pGetCharWidth32A(hdc, first, last, buf);
}

static BOOL WINAPI H_GetTextExtentPoint32A(HDC hdc, LPCSTR str, int c, LPSIZE sz) {
    if (str && c > 0) {
        int wn = 0;
        wchar_t *ui = lookup_ui(str, c, &wn);
        if (ui) {
            BOOL ok = GetTextExtentPoint32W(hdc, ui, wn, sz);
            HeapFree(GetProcessHeap(), 0, ui);
            return ok;
        }
    }
    if (str && c >= 2 && has_gbk_pair(str, c)) {
        int wn = 0;
        wchar_t *w = to_wide(936, str, c, &wn);
        if (w) {
            BOOL ok = GetTextExtentPoint32W(hdc, w, wn, sz);
            HeapFree(GetProcessHeap(), 0, w);
            return ok;
        }
    }
    return pGetTextExtentPoint32A(hdc, str, c, sz);
}

static int WINAPI H_DrawTextA(HDC hdc, LPCSTR str, int c, LPRECT rc, UINT fmt) {
    int n = c;
    if (str && n < 0)
        n = lstrlenA(str);
    if (str && n > 0) {
        int wn = 0;
        wchar_t *ui = lookup_ui(str, n, &wn);
        if (ui) {
            int r = DrawTextW(hdc, ui, wn, rc, fmt);
            HeapFree(GetProcessHeap(), 0, ui);
            return r;
        }
    }
    if (str && n >= 2 && has_gbk_pair(str, n)) {
        int wn = 0;
        wchar_t *w = to_wide(936, str, n, &wn);
        if (w) {
            int r = DrawTextW(hdc, w, wn, rc, fmt);
            HeapFree(GetProcessHeap(), 0, w);
            return r;
        }
    }
    return pDrawTextA(hdc, str, c, rc, fmt);
}

static void *rva_to_ptr(BYTE *base, DWORD rva) { return base + rva; }

static int patch_iat_module(HMODULE mod, const char *dll, const char *fn, void *hook, void **saved) {
    BYTE *base = (BYTE *)mod;
    IMAGE_DOS_HEADER *dos;
    IMAGE_NT_HEADERS *nt;
    IMAGE_IMPORT_DESCRIPTOR *imp;
    DWORD imp_rva;

    dos = (IMAGE_DOS_HEADER *)base;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE)
        return 0;
    nt = (IMAGE_NT_HEADERS *)(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE)
        return 0;
    imp_rva = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress;
    if (!imp_rva)
        return 0;
    for (imp = (IMAGE_IMPORT_DESCRIPTOR *)rva_to_ptr(base, imp_rva); imp->Name; imp++) {
        char *name = (char *)rva_to_ptr(base, imp->Name);
        IMAGE_THUNK_DATA *oft, *ft;
        if (lstrcmpiA(name, dll) != 0)
            continue;
        oft = (IMAGE_THUNK_DATA *)rva_to_ptr(base, imp->OriginalFirstThunk ? imp->OriginalFirstThunk : imp->FirstThunk);
        ft = (IMAGE_THUNK_DATA *)rva_to_ptr(base, imp->FirstThunk);
        for (; oft->u1.AddressOfData; oft++, ft++) {
            IMAGE_IMPORT_BY_NAME *ibn;
            DWORD old;
            if (oft->u1.Ordinal & IMAGE_ORDINAL_FLAG)
                continue;
            ibn = (IMAGE_IMPORT_BY_NAME *)rva_to_ptr(base, (DWORD)oft->u1.AddressOfData);
            if (lstrcmpA((char *)ibn->Name, fn) != 0)
                continue;
            if (saved && !*saved)
                *saved = (void *)(ULONG_PTR)ft->u1.Function;
            VirtualProtect(&ft->u1.Function, sizeof(ft->u1.Function), PAGE_EXECUTE_READWRITE, &old);
            ft->u1.Function = (ULONG_PTR)hook;
            VirtualProtect(&ft->u1.Function, sizeof(ft->u1.Function), old, &old);
            return 1;
        }
    }
    return 0;
}

static void log_line(const char *s) {
    HANDLE f;
    DWORD n;
    f = CreateFileA("gdi_zh.log", FILE_APPEND_DATA, FILE_SHARE_READ, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f == INVALID_HANDLE_VALUE)
        return;
    WriteFile(f, s, (DWORD)lstrlenA(s), &n, NULL);
    WriteFile(f, "\r\n", 2, &n, NULL);
    CloseHandle(f);
}

/* Preferred image base is 0x10000; no ASLR. RVAs = VA - 0x10000. */
#define RVA_DECODE 0x00022750
#define RVA_D3DGLYPH 0x00028720
#define RVA_FONT 0x0014482D8
#define RVA_DEVICE 0x001120F8C
#define RVA_COLOR 0x000D8B130
#define RVA_COLORMASK 0x0001AA3C8
#define CJK_INDEX 1

static BYTE *g_mod;
static void *g_decode_tramp;
static unsigned char g_has_cjk;
static wchar_t g_cjk;
static float g_x, g_y, g_sc;
static BYTE g_color;
static int g_cjk_n;
static BYTE g_bits[128 * 16];
static volatile LONG g_hooked;

static int ptr_ok(const void *p, SIZE_T n) {
    MEMORY_BASIC_INFORMATION m;
    const BYTE *b, *e;
    if (!p || n == 0)
        return 0;
    b = (const BYTE *)p;
    e = b + n - 1;
    if (!VirtualQuery(p, &m, sizeof(m)))
        return 0;
    if (m.State != MEM_COMMIT)
        return 0;
    if (m.Protect & (PAGE_NOACCESS | PAGE_GUARD))
        return 0;
    if (e >= (const BYTE *)m.BaseAddress + m.RegionSize) {
        if (!VirtualQuery(e, &m, sizeof(m)))
            return 0;
        if (m.State != MEM_COMMIT || (m.Protect & (PAGE_NOACCESS | PAGE_GUARD)))
            return 0;
    }
    return 1;
}

static int is_cjk_wc(wchar_t wc) {
    return (wc >= 0x2E80 && wc <= 0x9FFF) || (wc >= 0xF900 && wc <= 0xFAFF) ||
           (wc >= 0x3000 && wc <= 0x303F) || (wc >= 0xFF01 && wc <= 0xFF60);
}

static void *alloc_exec(int n) {
    return VirtualAlloc(NULL, (SIZE_T)n, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
}

static void emit_jmp(BYTE *at, BYTE *to) {
    DWORD old;
    VirtualProtect(at, 8, PAGE_EXECUTE_READWRITE, &old);
    at[0] = 0xE9;
    *(DWORD *)(at + 1) = (DWORD)(to - (at + 5));
    VirtualProtect(at, 8, old, &old);
    FlushInstructionCache(GetCurrentProcess(), at, 8);
}

static void *make_tramp(BYTE *src, int stolen, BYTE *cont) {
    BYTE *t = (BYTE *)alloc_exec(32);
    if (!t)
        return NULL;
    memcpy(t, src, stolen);
    t[stolen] = 0xE9;
    *(DWORD *)(t + stolen + 1) = (DWORD)(cont - (t + stolen + 5));
    return t;
}

static unsigned char orig_decode(char **p) {
    unsigned char r;
    void *fn = g_decode_tramp;
    __asm__ __volatile__(
        "movl %1, %%ecx\n\t"
        "call *%2\n\t"
        : "=a"(r)
        : "r"(p), "m"(fn)
        : "ecx", "edx", "esi", "edi", "memory");
    return r;
}

static void install_cjk_glyph(wchar_t wc) {
    BYTE *font;
    short *slot;
    int h, w, x, y, stride, ave;
    HDC hdc;
    HFONT hf, oldf;
    HBITMAP bm, oldb;
    BITMAPINFO bi;
    TEXTMETRICA tm;
    RECT rc;
    DWORD pix[128 * 64];
    DWORD *pd;

    font = g_mod ? *(BYTE **)(g_mod + RVA_FONT) : NULL;
    if (!font || !ptr_ok(font, 0x12 + CJK_INDEX * 8 + 8))
        return;
    h = *(short *)(font + 8);
    ave = *(short *)(font + 0xa);
    if (h < 10)
        h = 16;
    if (h > 64)
        h = 64;
    if (ave < 4)
        ave = h / 2;
    /* Overlay advances one Latin cell per decoded byte. CJK must take two
       cells; a variable em-width clips the last glyph of short labels. */
    w = ave * 2;
    if (w > 127)
        w = 127;

    hdc = CreateCompatibleDC(NULL);
    hf = CreateFontA(-h, 0, 0, 0, FW_NORMAL, 0, 0, 0, 134, 0, 0, 4, 0, "SimHei");
    oldf = (HFONT)SelectObject(hdc, hf);
    GetTextMetricsA(hdc, &tm);
    bm = CreateCompatibleBitmap(hdc, w, h);
    oldb = (HBITMAP)SelectObject(hdc, bm);
    rc.left = 0;
    rc.top = 0;
    rc.right = w;
    rc.bottom = h;
    FillRect(hdc, &rc, (HBRUSH)GetStockObject(BLACK_BRUSH));
    SetBkMode(hdc, TRANSPARENT);
    SetTextColor(hdc, RGB(255, 255, 255));
    SetTextAlign(hdc, TA_BASELINE | TA_LEFT);
    ExtTextOutW(hdc, 0, tm.tmAscent, 0, NULL, &wc, 1, NULL);
    memset(&bi, 0, sizeof(bi));
    bi.bmiHeader.biSize = 40;
    bi.bmiHeader.biWidth = w;
    bi.bmiHeader.biHeight = -h;
    bi.bmiHeader.biPlanes = 1;
    bi.bmiHeader.biBitCount = 32;
    GetDIBits(hdc, bm, 0, h, pix, &bi, DIB_RGB_COLORS);
    stride = (w + 7) >> 3;
    memset(g_bits, 0, (unsigned)stride * (unsigned)h);
    pd = pix;
    for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
            if ((pd[y * w + x] & 0xFF) > 40)
                g_bits[y * stride + (x >> 3)] |= (BYTE)(0x80 >> (x & 7));
        }
    }
    slot = (short *)(font + 0x12 + CJK_INDEX * 8);
    slot[0] = (short)w;
    slot[1] = (short)h;
    *(BYTE **)(slot + 2) = g_bits;
    SelectObject(hdc, oldb);
    SelectObject(hdc, oldf);
    DeleteObject(bm);
    DeleteObject(hf);
    DeleteDC(hdc);
}

static int gdi_text_on_surface(void *surf, int x, int y, wchar_t wc, DWORD argb, int h) {
    void **vt;
    HDC hdc;
    HRESULT hr;
    HFONT hf, oldf;

    if (!surf || !ptr_ok(surf, sizeof(void *)))
        return 0;
    vt = *(void ***)surf;
    if (!ptr_ok(vt, 17 * sizeof(void *)) || !vt[15] || !vt[16])
        return 0;
    hdc = NULL;
    hr = ((HRESULT(WINAPI *)(void *, HDC *))vt[15])(surf, &hdc);
    if (hr < 0 || !hdc)
        return 0;
    if (h < 10)
        h = 16;
    hf = CreateFontA(-h, 0, 0, 0, FW_NORMAL, 0, 0, 0, 134, 0, 0, 4, 0, "SimHei");
    oldf = (HFONT)SelectObject(hdc, hf);
    SetBkMode(hdc, TRANSPARENT);
    SetTextColor(hdc, RGB((argb >> 16) & 0xFF, (argb >> 8) & 0xFF, argb & 0xFF));
    ExtTextOutW(hdc, x, y, 0, NULL, &wc, 1, NULL);
    SelectObject(hdc, oldf);
    DeleteObject(hf);
    ((HRESULT(WINAPI *)(void *, HDC))vt[16])(surf, hdc);
    return 1;
}

static ULONG surf_release(void *surf) {
    void **vt;
    if (!surf || !ptr_ok(surf, sizeof(void *)))
        return 0;
    vt = *(void ***)surf;
    if (!ptr_ok(vt, 3 * sizeof(void *)) || !vt[2])
        return 0;
    return ((ULONG(WINAPI *)(void *))vt[2])(surf);
}

void draw_cjk_d3d(void) {
    void *dev, *rt, *off;
    void **vt;
    DWORD argb, mask;
    int h, x, y, ok, w;
    BYTE *font;
    RECT src, dst;
    char msg[96];

    g_has_cjk = 0;
    if (!g_mod || !ptr_ok(g_mod + RVA_DEVICE, sizeof(void *)))
        return;
    font = ptr_ok(g_mod + RVA_FONT, sizeof(void *)) ? *(BYTE **)(g_mod + RVA_FONT) : NULL;
    h = font ? *(short *)(font + 8) : 16;
    if (h < 10)
        h = 16;
    w = h;
    x = (int)g_x;
    y = (int)g_y;
    mask = *(DWORD *)(g_mod + RVA_COLORMASK);
    argb = ((DWORD *)(g_mod + RVA_COLOR))[g_color] & mask;
    if (!argb)
        argb = 0xFFFFFFFF;
    dev = *(void **)(g_mod + RVA_DEVICE);
    ok = 0;
    rt = NULL;
    off = NULL;
    if (dev && ptr_ok(dev, sizeof(void *))) {
        vt = *(void ***)dev;
        if (!ptr_ok(vt, 39 * sizeof(void *)) || !vt[38])
            return;
        if (((HRESULT(WINAPI *)(void *, DWORD, void **))vt[38])(dev, 0, &rt) >= 0 && rt)
            ok = gdi_text_on_surface(rt, x, y, g_cjk, argb, h);
        if (!ok && rt) {
            /* Copy dest pixels into an offscreen surface, GDI-draw CJK, blit back.
               D3DFMT_X8R8G8B8=22, D3DPOOL_DEFAULT=0, filter POINT=1. */
            if (((HRESULT(WINAPI *)(void *, UINT, UINT, DWORD, DWORD, void **, void *))vt[36])(dev, (UINT)w, (UINT)h, 22, 0,
                                                                                             &off, NULL) >= 0 &&
                off) {
                src.left = 0;
                src.top = 0;
                src.right = w;
                src.bottom = h;
                dst.left = x;
                dst.top = y;
                dst.right = x + w;
                dst.bottom = y + h;
                ((HRESULT(WINAPI *)(void *, void *, RECT *, void *, RECT *, DWORD))vt[34])(dev, rt, &dst, off, &src, 0);
                if (gdi_text_on_surface(off, 0, 0, g_cjk, argb, h) &&
                    ((HRESULT(WINAPI *)(void *, void *, RECT *, void *, RECT *, DWORD))vt[34])(dev, off, &src, rt, &dst, 1) >=
                        0)
                    ok = 2;
            }
        }
        if (!ok) {
            void *bb = NULL;
            if (((HRESULT(WINAPI *)(void *, UINT, UINT, DWORD, void **))vt[18])(dev, 0, 0, 0, &bb) >= 0 && bb) {
                ok = gdi_text_on_surface(bb, x, y, g_cjk, argb, h) ? 3 : 0;
                surf_release(bb);
            }
        }
    }
    surf_release(off);
    surf_release(rt);
    g_cjk_n++;
    if (g_cjk_n <= 12) {
        wsprintfA(msg, "cjk U+%04X path=%d xy=%d,%d h=%d col=%08X", (unsigned)g_cjk, ok, x, y, h, argb);
        log_line(msg);
    }
}

static unsigned char H_decode(char **p) {
    unsigned char *s;
    unsigned char b;
    wchar_t wc;

    if (!p || !*p)
        return orig_decode(p);
    s = (unsigned char *)*p;
    b = s[0];
    if (!b)
        return orig_decode(p);

    /* GBK fullwidth ASCII (A3A1-A3FE) -> Latin so ':' matches overlay metrics. */
    if (b == 0xA3 && s[1] >= 0xA1 && s[1] <= 0xFE) {
        *p = (char *)(s + 2);
        g_has_cjk = 0;
        return (unsigned char)(s[1] - 0x80);
    }

    /* GBK before C2/C3: 美/轮/夺 start with C3/C2 and became '?'.
       Only accept real CJK so high Latin bytes are not eaten (that desyncs the walker). */
    if (is_lead(b) && s[1] && is_trail(s[1])) {
        if (MultiByteToWideChar(936, 0, (char *)s, 2, &wc, 1) == 1 && is_cjk_wc(wc)) {
            *p = (char *)(s + 2);
            g_cjk = wc;
            g_has_cjk = 1;
            install_cjk_glyph(wc);
            return CJK_INDEX;
        }
    }
    return orig_decode(p);
}

static void install_inline_hooks(void) {
    BYTE *decode, *d3d, *stub, *p;
    char msg[80];

    g_mod = (BYTE *)GetModuleHandleA(NULL);
    if (!g_mod)
        return;
    /* Confirm → 3D reset: a leftover CJK flag made the D3D hook GetDC the
       backbuffer during load and crash. Overlay text stays English. */
    log_line("inline hooks off (confirm-safe)");
    return;
    decode = g_mod + RVA_DECODE;
    d3d = g_mod + RVA_D3DGLYPH;
    if (decode[0] != 0x56 || d3d[0] != 0x53) {
        wsprintfA(msg, "inline skip decode=%02X d3d=%02X", decode[0], d3d[0]);
        log_line(msg);
        return;
    }
    g_decode_tramp = make_tramp(decode, 6, decode + 6);

    /* Preserve ebx/esi/edi: TCC and the walker both use them; clobber = crash after CJK. */
    stub = (BYTE *)alloc_exec(48);
    p = stub;
    *p++ = 0x53;
    *p++ = 0x56;
    *p++ = 0x57;
    *p++ = 0x51;
    *p++ = 0xE8;
    *(DWORD *)p = (DWORD)((BYTE *)H_decode - (p + 4));
    p += 4;
    *p++ = 0x83;
    *p++ = 0xC4;
    *p++ = 0x04;
    *p++ = 0x5F;
    *p++ = 0x5E;
    *p++ = 0x5B;
    *p++ = 0xC3;
    emit_jmp(decode, stub);

    stub = (BYTE *)alloc_exec(96);
    p = stub;
    *p++ = 0x60; /* pushad around CJK draw */
    /* movss [g_x], xmm1 */
    *p++ = 0xF3;
    *p++ = 0x0F;
    *p++ = 0x11;
    *p++ = 0x0D;
    *(DWORD *)p = (DWORD)&g_x;
    p += 4;
    *p++ = 0xF3;
    *p++ = 0x0F;
    *p++ = 0x11;
    *p++ = 0x15;
    *(DWORD *)p = (DWORD)&g_y;
    p += 4;
    *p++ = 0xF3;
    *p++ = 0x0F;
    *p++ = 0x11;
    *p++ = 0x1D;
    *(DWORD *)p = (DWORD)&g_sc;
    p += 4;
    *p++ = 0x88;
    *p++ = 0x15;
    *(DWORD *)p = (DWORD)&g_color;
    p += 4;
    *p++ = 0x80;
    *p++ = 0x3D;
    *(DWORD *)p = (DWORD)&g_has_cjk;
    p += 4;
    *p++ = 0x00;
    *p++ = 0x74;
    *p++ = 7; /* skip call + popad + ret */
    *p++ = 0xE8;
    *(DWORD *)p = (DWORD)((BYTE *)draw_cjk_d3d - (p + 4));
    p += 4;
    *p++ = 0x61; /* popad */
    *p++ = 0xC3;
    *p++ = 0x61; /* popad, then original glyph */
    memcpy(p, d3d, 6);
    p += 6;
    *p++ = 0xE9;
    *(DWORD *)p = (DWORD)((d3d + 6) - (p + 4));
    emit_jmp(d3d, stub);

    log_line("inline decode+d3d glyph hooked");
}

static void install_hooks(void);

static void install_hooks_once(void) {
    if (InterlockedCompareExchange(&g_hooked, 1, 0) != 0)
        return;
    install_hooks();
}

static void install_hooks(void) {
    char msg[80];
    HMODULE exe = GetModuleHandleA(NULL);
    HMODULE gdi = GetModuleHandleA("gdi32.dll");
    HMODULE usr = GetModuleHandleA("user32.dll");
    if (gdi) {
        pExtTextOutA = (ExtTextOutA_t)GetProcAddress(gdi, "ExtTextOutA");
        pTextOutA = (TextOutA_t)GetProcAddress(gdi, "TextOutA");
        pGetCharWidth32A = (GetCharWidth32A_t)GetProcAddress(gdi, "GetCharWidth32A");
        pGetTextExtentPoint32A = (GetTextExtentPoint32A_t)GetProcAddress(gdi, "GetTextExtentPoint32A");
    }
    if (usr)
        pDrawTextA = (DrawTextA_t)GetProcAddress(usr, "DrawTextA");

    wsprintfA(msg, "hook ExtTextOutA=%d TextOutA=%d Width=%d Extent=%d DrawText=%d",
              patch_iat_module(exe, "GDI32.dll", "ExtTextOutA", (void *)H_ExtTextOutA, (void **)&pExtTextOutA),
              patch_iat_module(exe, "GDI32.dll", "TextOutA", (void *)H_TextOutA, (void **)&pTextOutA),
              patch_iat_module(exe, "GDI32.dll", "GetCharWidth32A", (void *)H_GetCharWidth32A, (void **)&pGetCharWidth32A),
              patch_iat_module(exe, "GDI32.dll", "GetTextExtentPoint32A", (void *)H_GetTextExtentPoint32A,
                               (void **)&pGetTextExtentPoint32A),
              patch_iat_module(exe, "USER32.dll", "DrawTextA", (void *)H_DrawTextA, (void **)&pDrawTextA));
    log_line(msg);
    install_inline_hooks();
}

static DWORD WINAPI late_hook(LPVOID p) {
    (void)p;
    /* Do not patch .text inside DllMain (loader lock / Steam overlay). */
    Sleep(200);
    install_hooks_once();
    return 0;
}

static HMODULE load_sys_dinput8(void) {
    wchar_t path[MAX_PATH];
    UINT n = GetSystemDirectoryW(path, MAX_PATH);
    if (!n || n >= MAX_PATH - 16)
        return NULL;
    lstrcatW(path, L"\\dinput8.dll");
    return LoadLibraryW(path);
}

__declspec(dllexport) HRESULT WINAPI DirectInput8Create(HINSTANCE a, DWORD b, const void *c, LPVOID *d, LPVOID e) {
    install_hooks_once();
    if (!g_DirectInput8Create) {
        if (!g_dinput)
            g_dinput = load_sys_dinput8();
        if (g_dinput)
            g_DirectInput8Create = (DirectInput8Create_t)GetProcAddress(g_dinput, "DirectInput8Create");
    }
    if (!g_DirectInput8Create)
        return E_FAIL;
    return g_DirectInput8Create(a, b, c, d, e);
}

BOOL APIENTRY DllMain(HINSTANCE inst, DWORD reason, LPVOID res) {
    (void)inst;
    (void)res;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(inst);
        InitializeCriticalSection(&g_cs);
        log_line("gdi_zh attached (no rdata patch)");
        /* Do not patch exe LOADING * strings: the remaster matches them when
           Confirm starts a mission. Draw-time lookup_ui already remaps GDI. */
        CloseHandle(CreateThread(NULL, 0, late_hook, NULL, 0, NULL));
    } else if (reason == DLL_PROCESS_DETACH) {
        DeleteCriticalSection(&g_cs);
    }
    return TRUE;
}
