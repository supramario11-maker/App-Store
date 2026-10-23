import Foundation

struct AppItem: Identifiable, Codable {
    let id: UUID
    let title: String
    let subtitle: String
    let version: String
    let ipaURL: URL?
    let iconName: String
    let manifestName: String // Links directly to the matching manifest file name on GitHub Pages
}
