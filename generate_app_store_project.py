import os

def create_app_store_files():
    # Setup correct Apple-compliant directories
    dirs = [
        "AppStoreProject",
        "AppStoreProject/Models",
        "AppStoreProject/Views",
        "AppStoreProject/Services",
        "AppStoreProject/SupportingFiles"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Create App Data Model
    model_code = """import Foundation

struct AppItem: Identifiable, Codable {
    let id: UUID
    let title: String
    let subtitle: String
    let version: String
    let ipaURL: URL?
    let iconName: String
}
"""
    with open("AppStoreProject/Models/AppItem.swift", "w") as f:
        f.write(model_code)

    # 2. Create Interface with '+' Button
    view_code = """import SwiftUI
import UniformTypeIdentifiers

struct MainStoreView: View {
    @State private var availableApps: [AppItem] = [
        AppItem(id: UUID(), title: "Roblox", subtitle: "Play Millions of Games", version: "2.640.0", ipaURL: nil, iconName: "gamecontroller"),
        AppItem(id: UUID(), title: "Dr. Driving", subtitle: "Dr. Driving drives you crazy!", version: "1.69", ipaURL: nil, iconName: "car"),
        AppItem(id: UUID(), title: "Combat Master", subtitle: "Fast-Paced Action FPS", version: "0.12.3", ipaURL: nil, iconName: "shield")
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
                        print("Signing app package locally: \\(app.title)")
                    }
                    .font(.system(size: 14, weight: .bold))
                    .padding(.horizontal, 20)
                    .padding(.vertical, 6)
                    .background(Color(.systemGroupedBackground))
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
            let newApp = AppItem(id: UUID(), title: name, subtitle: "Local Unsigned IPA", version: "1.0", ipaURL: url, iconName: "doc.badge.plus")
            parent.apps.append(newApp)
        }
    }
}
"""
    with open("AppStoreProject/Views/MainStoreView.swift", "w") as f:
        f.write(view_code)

    # 3. Create Clean Lifecycle Launcher Entry Point
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

    # 4. Create Essential Plist Targets File
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

    # 5. Correctly Setup Project Schema file for XcodeGen
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

    print("\n[Success] Complete source setup script files generated successfully!")

if __name__ == "__main__":
    create_app_store_files()
