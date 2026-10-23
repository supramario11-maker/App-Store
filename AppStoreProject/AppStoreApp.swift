if let url = app.ipaURL {
    downloadManager.downloadIPA(
        from: url,
        title: app.title
    )
}
