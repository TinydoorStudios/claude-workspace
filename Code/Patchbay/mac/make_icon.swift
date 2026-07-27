// make_icon.swift — renders Patchbay's app icon (a patchbay jack field with one
// cable run) into an .iconset directory. Run by make_icon.sh, which then calls
// iconutil. Usage: swift make_icon.swift <output-iconset-dir>

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

    // dark panel background, matching the app's dark theme
    let inset = s * 0.045
    let rect = NSRect(x: inset, y: inset, width: s - 2 * inset, height: s - 2 * inset)
    let bg = NSBezierPath(roundedRect: rect, xRadius: s * 0.2, yRadius: s * 0.2)
    let grad = NSGradient(starting: NSColor(srgbRed: 0.07, green: 0.08, blue: 0.10, alpha: 1),
                          ending:   NSColor(srgbRed: 0.12, green: 0.15, blue: 0.19, alpha: 1))!
    grad.draw(in: bg, angle: -90)
    bg.setClip()

    // two rows of jacks
    let cols = 6
    let margin = s * 0.16
    let span = s - 2 * margin
    let gap = span / CGFloat(cols - 1)
    let rowY: [CGFloat] = [s * 0.635, s * 0.365]
    let jackR = s * 0.052

    func center(_ col: Int, _ row: Int) -> NSPoint {
        NSPoint(x: margin + CGFloat(col) * gap, y: rowY[row])
    }

    for row in 0..<2 {
        for col in 0..<cols {
            let c = center(col, row)
            let ring = NSBezierPath(ovalIn: NSRect(x: c.x - jackR, y: c.y - jackR,
                                                   width: jackR * 2, height: jackR * 2))
            NSColor(srgbRed: 0.20, green: 0.24, blue: 0.29, alpha: 1).setFill()
            ring.fill()
            let holeR = jackR * 0.52
            let hole = NSBezierPath(ovalIn: NSRect(x: c.x - holeR, y: c.y - holeR,
                                                   width: holeR * 2, height: holeR * 2))
            NSColor(srgbRed: 0.04, green: 0.05, blue: 0.06, alpha: 1).setFill()
            hole.fill()
        }
    }

    // one patched pair, lit in the DiGiCo blue, with a cable slung between them
    let from = center(1, 0)
    let to = center(4, 1)
    let live = NSColor(srgbRed: 0.42, green: 0.68, blue: 0.92, alpha: 1)

    let cable = NSBezierPath()
    cable.move(to: from)
    cable.curve(to: to,
                controlPoint1: NSPoint(x: from.x + gap * 0.4, y: from.y - s * 0.28),
                controlPoint2: NSPoint(x: to.x - gap * 0.4, y: to.y - s * 0.24))
    cable.lineWidth = s * 0.038
    cable.lineCapStyle = .round
    live.withAlphaComponent(0.95).setStroke()
    cable.stroke()

    for c in [from, to] {
        let plug = NSBezierPath(ovalIn: NSRect(x: c.x - jackR, y: c.y - jackR,
                                               width: jackR * 2, height: jackR * 2))
        live.setFill()
        plug.fill()
        let holeR = jackR * 0.42
        let hole = NSBezierPath(ovalIn: NSRect(x: c.x - holeR, y: c.y - holeR,
                                               width: holeR * 2, height: holeR * 2))
        NSColor(srgbRed: 0.04, green: 0.06, blue: 0.09, alpha: 1).setFill()
        hole.fill()
    }

    NSGraphicsContext.restoreGraphicsState()
    return rep
}

for (name, px) in specs {
    let rep = draw(px)
    guard let data = rep.representation(using: .png, properties: [:]) else { continue }
    try? data.write(to: URL(fileURLWithPath: "\(out)/\(name).png"))
}
