package policy

type Risk string

const (
	RiskLow    Risk = "low"
	RiskMedium Risk = "medium"
	RiskHigh   Risk = "high"
)

var actionRisks = map[string]Risk{
	"system.status":     RiskLow,
	"filesystem.list":   RiskLow,
	"filesystem.read":   RiskLow,
	"filesystem.write":  RiskMedium,
	"filesystem.copy":   RiskMedium,
	"filesystem.move":   RiskMedium,
	"process.list":      RiskLow,
	"process.start":     RiskMedium,
	"process.stop":      RiskMedium,
	"shell.powershell":  RiskMedium,
	"screen.screenshot": RiskLow,
	"ui.snapshot":       RiskLow,
	"ui.invoke":         RiskMedium,
	"ui.click":          RiskMedium,
	"ui.type":           RiskMedium,
	"ui.shortcut":       RiskMedium,
	"app.launch":        RiskMedium,
	"app.switch":        RiskLow,
}

func riskForAction(action string) Risk {
	if risk, ok := actionRisks[action]; ok {
		return risk
	}
	return RiskHigh
}
