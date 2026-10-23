import os

def create_app_store_files():
    # Define project architecture directories
    dirs = [
        "AppStoreProject",
        "AppStoreProject/Models",
        "AppStoreProject/Views",
        "AppStoreProject/Services"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created directory: {d}")

    # 1. Create App Data Model
    model_code = """import Foundation

struct AppItem: Identifiable, Codable {
    let id: UUID
    let title: String
    let subtitle: String
    let version: String
    let ipaURL: URL
    let iconColorHex: String
}
"""
    with open("AppStoreProject/Models/AppItem.swift", "w") as f:
        f.write(model_code)

    # 2. Create Network and Download Service
    service_code = """import Foundation

class DownloadManager: NSObject, ObservableObject, URLSessionDownloadDelegate {
    @Published var progress: Float = 0.0
    @Published var isDownloading = false
    @Published var downloadedFileUrl: URL?

    func downloadIPA(from url: URL) {
        isDownloading = true
        progress = 0.0
        
        let session = URLSession(configuration: .default, delegate: self, delegateQueue: OperationQueue.main)
        let downloadTask = session.downloadTask(with: url)
        downloadTask.resume()
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didFinishDownloadingTo location: URL) {
        let fileManager = FileManager.default
        let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let destinationURL = documentsURL.appendingPathComponent("downloaded_app.ipa")
        
        try? fileManager.removeItem(at: destinationURL)
        do {
            try fileManager.moveItem(at: location, to: destinationURL)
            self.downloadedFileUrl = destinationURL
            print("IPA successfully stored at: \\(destinationURL.path)")
        } catch {
            print("File save error: \\(error.localizedDescription)")
        }
        isDownloading = false
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didWriteData bytesWritten: Int64, totalBytesWritten: Int64, totalBytesExpectedToWrite: Int64) {
        let calculatedProgress = Float(totalBytesWritten) / Float(totalBytesExpectedToWrite)
        DispatchQueue.main.async {
            self.progress = calculatedProgress
        }
    }
}
"""
    with open("AppStoreProject/Services/DownloadManager.swift", "w") as f:
        f.write(service_code)

    # 3. Create the Main App Interface View
    view_code = """import SwiftUI

struct MainStoreView: View {
    @StateObject private var downloadManager = DownloadManager()
    
    // Sample apps configuration list
    let availableApps = [
        AppItem(id: UUID(), title: "Sample Game", subtitle: "Action & Arcade", version: "1.0.4", ipaURL: URL(string: "https://yourserver.com")!, iconColorHex: "FF5E62"),
        AppItem(id: UUID(), title: "Development Utility", subtitle: "Developer Tools", version: "2.1.0", ipaURL: URL(string: "https://yourserver.com")!, iconColorHex: "007AFF")
    ]

    var body: some View {
        NavigationView {
            List(availableApps) { app in
                HStack(spacing: 16) {
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.blue) // Simple fallback block icon style
                        .frame(width: 60, height: 60)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(app.title).font(.headline).foregroundColor(.primary)
                        Text(app.subtitle).font(.subheadline).foregroundColor(.secondary)
                        Text("v\\(app.version)").font(.caption2).foregroundColor(.gray)
                    }
                    
                    Spacer()
                    
                    Button(action: {
                        downloadManager.downloadIPA(from: app.ipaURL)
                    }) {
                        Text("GET")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(.blue)
                            .padding(.horizontal, 20)
                            .padding(.vertical, 6)
                            .background(Color(.systemGroupedBackground))
                            .cornerRadius(20)
                    }
                }
                .padding(.vertical, 4)
            }
            .navigationTitle("Custom Store")
            .overlay(
                Group {
                    if downloadManager.isDownloading {
                        ZStack {
                            Color.black.opacity(0.4).edgesIgnoringSafeArea(.all)
                            VStack(spacing: 16) {
                                ProgressView(value: downloadManager.progress)
                                    .progressViewStyle(LinearProgressViewStyle())
                                    .frame(width: 200)
                                Text("Downloading Package... \\(Int(downloadManager.progress * 100))%")
                                    .foregroundColor(.white)
                                    .font(.subheadline)
                            }
                            .padding()
                            .background(Color(.darkGray))
                            .cornerRadius(12)
                        }
                    }
                }
            )
        }
    }
}
"""
    with open("AppStoreProject/Views/MainStoreView.swift", "w") as f:
        f.write(view_code)

    print("\\n[Success] Your complete App Store engine source configuration files have been generated!")

if __name__ == "__main__":
    create_app_store_files()
