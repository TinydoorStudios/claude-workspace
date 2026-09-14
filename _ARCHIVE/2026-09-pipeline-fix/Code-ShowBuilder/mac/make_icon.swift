// make_icon.swift — renders ShowBuilder's app icon (an EQ curve on DiGiCo navy)
// into an .iconset directory. Run by make_icon.sh, which then calls iconutil.
// Usage: swift make_icon.swift <output-iconset-dir>

import AppKit

guard CommandLine.arguments.count > 1 else {
    FileHandle.standardError.write("usage: make_icon.swift <iconset-dir>\n".data(using: .utf8)!)
    exit(1)
}
let out = CommandLine.arguments[1]

let specs: [(String, Int)] = [
    ("icon_16x16", 16), ("icon_16x16@2x", 32),
    ("icon_32x32", 32), ("icon_32x32@2x", 64),
    ("icon_128x128", 128), ("icon_128x128@2x", 256),
    ("icon_256x256", 256), ("icon_256x256@2x", 512),
    ("icon_512x512", 512), ("icon_512x512@2x", 1024),
]

func draw(_ px: Int) -> NSBitmapImageRep {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: px, pixelsHigh: px,
                              bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true,
                              isPlanar: false, colorSpaceName: .deviceRGB,
                              bytesPerRow: 0, bitsPerPixel: 0)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
    let s = CGFloat(px)

    // rounded-rect background with a vertical navy gradient
    let inset = s * 0.045
    let rect = NSRect(x: inset, y: inset, width: s - 2 * inset, height: s - 2 * inset)
    let radius = s * 0.2
    let bg = NSBezierPath(roundedRect: rect, xRadius: radius, yRadius: radius)
    let grad = NSGradient(starting: NSColor(srgbRed: 0.06, green: 0.16, blue: 0.25, alpha: 1),
                          ending:   NSColor(srgbRed: 0.11, green: 0.25, blue: 0.40, alpha: 1))!
    grad.draw(in: bg, angle: -90)
    bg.setClip()

    let midY = s * 0.5
    let amp = s * 0.17

    // faint baseline
    let base = NSBezierPath()
    base.move(to: NSPoint(x: s * 0.13, y: midY))
    base.line(to: NSPoint(x: s * 0.87, y: midY))
    NSColor(white: 1, alpha: 0.22).setStroke()
    base.lineWidth = max(1, s * 0.012)
    base.stroke()

    // EQ curve: one boost bump, one cut dip
    let curve = NSBezierPath()
    let n = 220
    for i in 0...n {
        let t = CGFloat(i) / CGFloat(n)
        let x = s * (0.13 + 0.74 * t)
        let bump = amp * exp(-pow((t - 0.33) / 0.12, 2))
        let dip = amp * 0.9 * exp(-pow((t - 0.70) / 0.12, 2))
        let y = midY + bump - dip
        if i == 0 { curve.move(to: NSPoint(x: x, y: y)) }
        else { curve.line(to: NSPoint(x: x, y: y)) }
    }
    NSColor(srgbRed: 0.38, green: 0.64, blue: 0.88, alpha: 1).setStroke()
    curve.lineWidth = max(1.5, s * 0.05)
    curve.lineCapStyle = .round
    curve.lineJoinStyle = .round
    curve.stroke()

    NSGraphicsContext.restoreGraphicsState()
    return rep
}

for (name, px) in specs {
    let rep = draw(px)
    guard let data = rep.representation(using: .png, properties: [:]) else { continue }
    try! data.write(to: URL(fileURLWithPath: "\(out)/\(name).png"))
}
print("icons written to \(out)")
