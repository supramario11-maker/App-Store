import SwiftUI
struct MainStoreView: View {
    @StateObject private var downloadManager = DownloadManager()
    let availableApps = [
        AppItem(id: UUID(), title: "Sample Game", subtitle: "Arcade", version: "1.0.0", ipaURL: URL(string: "https://server.com")!, iconColorHex: "007AFF")
    ]
    var body: some View {
        NavigationView {
            List(availableApps) { app in
                HStack {
                    RoundedRectangle(cornerRadius: 12).fill(Color.blue).frame(width: 60, height: 60)
                    VStack(alignment: .leading) {
                        Text(app.title).font(.headline)
                        Text(app.subtitle).font(.subheadline).foregroundColor(.secondary)
                    }
                    Spacer()
                    Button("GET") { downloadManager.downloadIPA(from: app.ipaURL) }
                }
            }.navigationTitle("App Store")
        }
    }
}