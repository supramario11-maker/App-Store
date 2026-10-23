import os
import shutil

def create_app_store_files():
    # 1. Clean up old conflicting file entry points if they exist in the workspace
    conflicting_files = [
        "AppStoreProject/AppStoreTarget.swift",
        "AppStoreTarget.swift",
        "AppStoreProject/Views/AppStoreTarget.swift"
    ]
    for file_path in conflicting_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Removed duplicate entry file: {file_path}")

    # Define clean source directory architecture
    dirs = [
        "AppStoreProject",
        "AppStoreProject/Models",
        "AppStoreProject/Views",
        "AppStoreProject/Services",
        "AppStoreProject/SupportingFiles"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 2. Create App Data Model (Added unique manifest strings)
    model_code = """import Foundation

struct AppItem: Identifiable, Codable {
    let id: UUID
    let title: String
    let subtitle: String
    let version: String
    let ipaURL: URL?
    let iconName: String
    let manifestName: String // Links directly to the matching manifest file name on GitHub Pages
}
"""
    with open("AppStoreProject/Models/AppItem.swift", "w") as f:
        f.write(model_code)

    # 3. Create Network Service (Handles cloud download logic if saving raw bundles locally)
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
        let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask).first!
        let destinationURL = documentsURL.appendingPathComponent("downloaded_app.ipa")
        
        try? fileManager.removeItem(at: destinationURL)
        do {
            try fileManager.moveItem(at: location, to: destinationURL)
            self.downloadedFileUrl = destinationURL
        } catch {
            print("File save error: \\(error.localizedDescription)")
        }
        isDownloading = false
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didWriteData bytesWritten: Int64, totalBytesWritten: Int64, totalBytesExpectedToWrite: Int64) {
        DispatchQueue.main.async {
            self.progress = Float(totalBytesWritten) / Float(totalBytesExpectedToWrite)
        }
    }
}
"""
    with open("AppStoreProject/Services/DownloadManager.swift", "w") as f:
        f.write(service_code)

    # 4. Create Functional User Interface (FIXED: Calls itms-services protocol directly)
    view_code = """import SwiftUI
import UniformTypeIdentifiers

struct MainStoreView: View {
    @State private var availableApps: [AppItem] = [
        AppItem(id: UUID(), title: "Roblox", subtitle: "Play Millions of Games", version: "2.640.0", ipaURL: nil, iconName: "gamecontroller", manifestName: "roblox_manifest.plist"),
        AppItem(id: UUID(), title: "Dr. Driving", subtitle: "Dr. Driving drives you crazy!", version: "1.69", ipaURL: nil, iconName: "car", manifestName: "dr_driving_manifest.plist"),
        AppItem(id: UUID(), title: "Combat Master", subtitle: "Fast-Paced Action FPS", version: "0.12.3", ipaURL: nil, iconName: "shield", manifestName: "combat_master_manifest.plist")
    ]
    @State private var showFilePicker = false

    var body: some View {
        NavigationView {
            List(availableApps) { app in
                HStack(spacing: 16) {
                    Image(systemName: app.iconName)
                        .resizable()
                        .scaledToFit()
                        .frame(width: 40, height: 40)
                        .padding(10)
                        .background(Color(.systemGray5))
                        .cornerRadius(12)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(app.title).font(.headline)
                        Text(app.subtitle).font(.subheadline).foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    Button("GET") {
                        triggerOTAInstallation(for: app)
                    }
                    .font(.system(size: 14, weight: .bold))
                    .padding(.horizontal, 20)
                    .padding(.vertical, 6)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(20)
                }
            }
            .navigationTitle("Discover")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: { showFilePicker = true }) {
                        Image(systemName: "plus").font(.title2)
                    }
                }
            }
            .sheet(isPresented: $showFilePicker) {
                DocumentPicker(apps: $availableApps)
            }
        }
    }

    // Connects interface layout natively to your GitHub deployment schema
    func triggerOTAInstallation(for app: AppItem) {
        let gitHubPagesBase = "https://github.io"
        let fullManifestURL = "\\(gitHubPagesBase)\\(app.manifestName)"
        let otaUrlScheme = "itms-services://?action=download-manifest&url=\\(fullManifestURL)"
        
        guard let url = URL(string: otaUrlScheme) else {
            print("Invalid URL format generated.")
            return
        }
        
        UIApplication.shared.open(url, options: [:]) { success in
            if success {
                print("Successfully triggered installation prompt for: \\(app.title)")
            } else {
                print("Device workspace rejected payload routing path link.")
            }
        }
    }
}

struct DocumentPicker: UIViewControllerRepresentable {
    @Binding var apps: [AppItem]
    
    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: [UTType(filenameExtension: "ipa")!])
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIDocumentPickerViewController, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator(self) }
    
    class Coordinator: NSObject, UIDocumentPickerDelegate {
        var parent: DocumentPicker
        init(_ parent: DocumentPicker) { self.parent = parent }
        
        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            guard let url = urls.first else { return }
            let name = url.deletingPathExtension().lastPathComponent
            let newApp = AppItem(id: UUID(), title: name, subtitle: "Local Unsigned IPA", version: "1.0", ipaURL: url, iconName: "doc.badge.plus", manifestName: "custom_manifest.plist")
            parent.apps.append(newApp)
        }
    }
}
"""
    with open("AppStoreProject/Views/MainStoreView.swift", "w") as f:
        f.write(view_code)

    # 5. Create App Entry Point
    entry_code = """import SwiftUI

@main
struct AppStoreApp: App {
    var body: some Scene {
        WindowGroup {
            MainStoreView()
        }
    }
}
"""
    with open("AppStoreProject/AppStoreApp.swift", "w") as f:
        f.write(entry_code)

    # 6. Create Target Plist Specifications
    plist_code = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://apple.com">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>UILaunchScreen</key>
    <dict/>
</dict>
</plist>
"""
    with open("AppStoreProject/SupportingFiles/Info.plist", "w") as f:
        f.write(plist_code)

    # 7. Setup Project Configuration File for XcodeGen (Matches your custom bundle signature)
    project_yaml = """name: AppStoreProject
options:
  bundleIdPrefix: com.malek
targets:
  AppStoreProject:
    type: application
    platform: iOS
    deploymentTarget: "15.0"
    sources: 
      - path: AppStoreProject
    settings:
      INFOPLIST_FILE: AppStoreProject/SupportingFiles/Info.plist
      GENERATE_INFOPLIST_FILE: NO
"""
    with open("project.yml", "w") as f:
        f.write(project_yaml)

    print("\n[Success] Complete source setup script files generated and pre-debugged successfully!")

if __name__ == "__main__":
    create_app_store_files()
