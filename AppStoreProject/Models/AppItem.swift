import Foundation

struct AppItem: Identifiable, Codable {
    let id: UUID
    let title: String
    let subtitle: String
    let version: String
    let ipaURL: URL?
    let iconName: String
}
